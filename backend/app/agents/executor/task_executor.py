"""
GEO-Industry-Engine Agent Task Executor
P0-A: DAG-based multi-step orchestration engine.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import asyncio
import time
from collections import defaultdict, deque


@dataclass
class TaskStep:
    """Single step in the execution DAG."""
    id: str
    agent_name: str
    tool_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    critical: bool = True
    timeout: int = 30
    description: str = ""

    def __hash__(self):
        return hash(self.id)


@dataclass
class StepResult:
    """Result of a single step execution."""
    step_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    retries: int = 0
    citations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Fully analyzed execution plan with DAG ordering."""
    steps: List[TaskStep]
    tiers: List[List[TaskStep]]
    total_steps: int = 0

    @classmethod
    def from_steps(cls, steps: List[TaskStep]) -> "ExecutionPlan":
        ids = [s.id for s in steps]
        if len(ids) != len(set(ids)):
            seen = set()
            dupes = [x for x in ids if x in seen or seen.add(x)]
            raise ValueError(f"Duplicate step ids: {dupes}")

        all_ids = set(ids)
        for s in steps:
            for dep in s.depends_on:
                if dep not in all_ids:
                    raise ValueError(f"Step '{s.id}' depends on unknown step '{dep}'")

        step_map = {s.id: s for s in steps}
        in_degree: Dict[str, int] = {s.id: len(s.depends_on) for s in steps}
        dependents: Dict[str, List[str]] = defaultdict(list)
        for s in steps:
            for dep in s.depends_on:
                dependents[dep].append(s.id)

        tiers: List[List[TaskStep]] = []
        queue = deque([sid for sid, deg in in_degree.items() if deg == 0])

        while queue:
            tier = [step_map[sid] for sid in sorted(queue)]
            tiers.append(tier)
            next_queue = deque()
            for step in tier:
                for dependent in dependents[step.id]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)
            queue = next_queue

        processed = sum(len(t) for t in tiers)
        if processed != len(steps):
            unprocessed = [sid for sid, deg in in_degree.items() if deg > 0]
            raise ValueError(f"Circular dependency detected: {unprocessed}")

        return cls(steps=steps, tiers=tiers, total_steps=len(steps))


class TaskExecutor:
    """DAG-based multi-step orchestrator."""

    def __init__(self, agent_registry=None):
        self._registry = agent_registry
        self._step_results: Dict[str, StepResult] = {}

    def set_registry(self, registry):
        self._registry = registry

    async def execute(self, plan: ExecutionPlan, db=None) -> Dict[str, Any]:
        self._step_results.clear()
        tier_outputs: Dict[str, Any] = {}

        for tier in plan.tiers:
            if len(tier) == 1:
                step = tier[0]
                result = await self._execute_step(step, tier_outputs, db)
                self._step_results[step.id] = result
                if result.success:
                    tier_outputs[step.id] = result.data
                elif step.critical:
                    return self._compile_failure(step.id, result.error or "step failed")
            else:
                results = await asyncio.gather(
                    *[self._execute_step(s, tier_outputs, db) for s in tier],
                    return_exceptions=True
                )
                for step, result in zip(tier, results):
                    if isinstance(result, Exception):
                        result = StepResult(step_id=step.id, success=False, error=str(result))
                    self._step_results[step.id] = result
                    if result.success:
                        tier_outputs[step.id] = result.data
                    elif step.critical:
                        return self._compile_failure(step.id, result.error or "step failed")

        return self._compile_success(plan, tier_outputs)

    async def _execute_step(self, step: TaskStep, previous_outputs: Dict[str, Any], db=None) -> StepResult:
        retries = 0
        last_error = None

        while retries <= 1:
            try:
                start = time.perf_counter()
                result_data = await asyncio.wait_for(
                    self._call_tool(step, previous_outputs, db),
                    timeout=step.timeout
                )
                elapsed = (time.perf_counter() - start) * 1000
                return StepResult(
                    step_id=step.id, success=True, data=result_data,
                    elapsed_ms=round(elapsed, 1), retries=retries
                )
            except asyncio.TimeoutError:
                last_error = f"Step '{step.id}' timed out after {step.timeout}s"
                retries += 1
            except Exception as e:
                last_error = str(e)
                retries += 1

        return StepResult(
            step_id=step.id, success=False, error=last_error or "unknown", retries=retries
        )

    async def _call_tool(self, step: TaskStep, previous_outputs: Dict[str, Any], db=None) -> Any:
        agent = self._registry.get(step.agent_name)
        if not agent:
            raise ValueError(f"Agent '{step.agent_name}' not found in registry")

        params = dict(step.params)
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$prev."):
                ref = value[6:]
                parts = ref.split(".", 1)
                prev_step_id = parts[0]
                prev_data = previous_outputs.get(prev_step_id)
                if prev_data is not None:
                    if len(parts) > 1:
                        params[key] = prev_data.get(parts[1], value)
                    else:
                        params[key] = prev_data

        tools = agent.get_tools()
        if step.tool_name not in tools:
            raise ValueError(f"Tool '{step.tool_name}' not registered on agent '{step.agent_name}'")

        return await tools[step.tool_name](**params)

    def _compile_success(self, plan: ExecutionPlan, outputs: Dict[str, Any]) -> Dict[str, Any]:
        step_results = {
            sid: {
                "success": r.success,
                "elapsed_ms": r.elapsed_ms,
                "retries": r.retries,
                "error": r.error,
            }
            for sid, r in self._step_results.items()
        }
        completed = sum(1 for r in self._step_results.values() if r.success)
        failed = sum(1 for r in self._step_results.values() if not r.success)
        return {
            "success": True,
            "total_steps": plan.total_steps,
            "completed_steps": completed,
            "failed_steps": failed,
            "step_results": step_results,
            "outputs": outputs,
            "execution_summary": self._build_summary(),
        }

    def _compile_failure(self, failed_step_id: str, error: str) -> Dict[str, Any]:
        step_results = {
            sid: {
                "success": r.success,
                "elapsed_ms": r.elapsed_ms,
                "retries": r.retries,
                "error": r.error,
            }
            for sid, r in self._step_results.items()
        }
        return {
            "success": False,
            "failed_step": failed_step_id,
            "error": error,
            "step_results": step_results,
            "execution_summary": self._build_summary(),
        }

    def _build_summary(self) -> str:
        completed = [sid for sid, r in self._step_results.items() if r.success]
        failed = [sid for sid, r in self._step_results.items() if not r.success]
        parts = []
        if completed:
            parts.append(f"{len(completed)} steps completed: {' -> '.join(completed)}")
        if failed:
            parts.append(f"{len(failed)} steps failed: {', '.join(failed)}")
        return " | ".join(parts) if parts else "No steps executed"


# Global singleton
task_executor = TaskExecutor()
