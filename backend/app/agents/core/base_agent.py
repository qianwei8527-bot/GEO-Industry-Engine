# GEO-Industry-Engine BaseAgent - P0-C: citation enforcement
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
import uuid
from datetime import datetime
from app.agents.memory.conversation_memory import ConversationMemory


@dataclass
class Citation:
    """P0-C: Traceable reference from agent output back to data source."""
    source: str           # Entity, Evidence, Event, DecisionRule, ContextEngine, DecisionEngine
    id: str = ""
    field: str = ""
    description: str = ""
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "id": self.id,
            "field": self.field,
            "description": self.description,
            "confidence": self.confidence,
        }


@dataclass
class AgentContext:
    agent_id: str = ''
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    input_query: str = ''
    intent: str = 'analyze'
    params: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentResult:
    """P0-C: Agent results MUST include citations."""
    agent_id: str = ''
    task_id: str = ''
    success: bool = True
    data: Any = None
    summary: str = ''
    error: Optional[str] = None
    tool_calls: List[str] = field(default_factory=list)
    chain_steps: List[Dict] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.utcnow)

    def add_citation(self, source: str, id: str = "", field: str = "",
                     description: str = "", confidence: float = 1.0):
        """Add a citation to this result."""
        self.citations.append(Citation(
            source=source, id=id, field=field,
            description=description, confidence=confidence
        ).to_dict())

    def validate_citations(self) -> bool:
        """Check that result has at least one citation (unless it's a failure)."""
        if not self.success:
            return True  # failures don't require citations
        if not self.citations:
            self.error = (self.error or "") + " [WARN: No citations provided]"
            return False
        return True


@dataclass
class ToolStep:
    """Multi-step execution step definition."""
    tool_name: str
    params: Dict[str, Any]
    description: str = ""
    depends_on: Optional[str] = None


class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.agent_id = f'agent-{name}-{uuid.uuid4().hex[:8]}'
        self.name = name
        self.description = description
        self._tools: Dict[str, Callable] = {}
        self._memory: List[AgentResult] = []
        self.conversation_memory = ConversationMemory()

    def register_tool(self, name: str, func: Callable):
        self._tools[name] = func

    def get_tools(self) -> Dict[str, Callable]:
        return self._tools

    async def use_tool(self, name: str, **kwargs) -> Any:
        """Single tool call (backward-compatible)."""
        if name not in self._tools:
            raise ValueError(f'Tool {name} not registered on agent {self.name}')
        result = await self._tools[name](**kwargs)
        self.conversation_memory.record(name, result, source="tool")
        return result

    async def execute_chain(self, ctx: AgentContext, steps: List[ToolStep]) -> AgentResult:
        """
        P0-C.3-2: Multi-step execution chain.
        Steps execute in order; previous step output passed to next step.
        """
        chain_results = []
        tool_calls = []
        previous_output = None

        for step in steps:
            params = dict(step.params)
            if step.depends_on and previous_output is not None:
                params["previous_result"] = previous_output
            params["memory_context"] = self.conversation_memory.get_context()

            try:
                result = await self.use_tool(step.tool_name, **params)
                chain_results.append({
                    "step": step.tool_name,
                    "description": step.description,
                    "success": True,
                    "result": result,
                })
                tool_calls.append(step.tool_name)
                previous_output = result
                if isinstance(result, dict) and result.get("error"):
                    break
            except Exception as e:
                chain_results.append({
                    "step": step.tool_name,
                    "description": step.description,
                    "success": False,
                    "error": str(e),
                })
                return AgentResult(
                    agent_id=self.agent_id,
                    task_id=ctx.task_id,
                    success=False,
                    error=f"Chain step '{step.tool_name}' failed: {e}",
                    tool_calls=tool_calls,
                    chain_steps=chain_results,
                )

        summary = self._compile_chain_summary(chain_results)
        result = AgentResult(
            agent_id=self.agent_id,
            task_id=ctx.task_id,
            success=True,
            data=chain_results,
            summary=summary,
            tool_calls=tool_calls,
            chain_steps=chain_results,
            metadata={"memory_snapshot": self.conversation_memory.snapshot()},
        )
        self.remember(result)
        return result

    def _compile_chain_summary(self, chain_results: List[Dict]) -> str:
        steps_done = [r["step"] for r in chain_results if r.get("success")]
        if not steps_done:
            return "No steps completed."
        return f"Chain completed {len(steps_done)} steps: {' -> '.join(steps_done)}"

    async def execute(self, ctx: AgentContext) -> AgentResult:
        """Single-step execution. Subclasses should override and add citations."""
        return await self.execute_chain(ctx, [])

    def remember(self, result: AgentResult):
        self._memory.append(result)
        if len(self._memory) > 100:
            self._memory = self._memory[-50:]

    def get_memory(self, limit: int = 10) -> List[AgentResult]:
        return self._memory[-limit:]

    @staticmethod
    def _safe_score(scores_dict: Dict, key: str, field: str = "score") -> float:
        """Safely extract score from nested dict/object, return 0.0 on failure."""
        try:
            val = scores_dict.get(key, {})
            if isinstance(val, dict):
                return float(val.get(field, 0) or 0)
            return float(getattr(val, field, 0) or 0)
        except (TypeError, ValueError, AttributeError):
            return 0.0

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.name})>'
