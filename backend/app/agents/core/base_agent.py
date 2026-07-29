# 参考: LangChain BaseAgent + CrewAI Agent 设计模式
# P0-C.3-2: 多步执行链 — execute_chain() 支持Tool链式调用 + Memory
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
import uuid
from datetime import datetime
from app.agents.memory.conversation_memory import ConversationMemory

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
    agent_id: str = ''
    task_id: str = ''
    success: bool = True
    data: Any = None
    summary: str = ''
    error: Optional[str] = None
    tool_calls: List[str] = field(default_factory=list)
    chain_steps: List[Dict] = field(default_factory=list)  # P0-C.3-2: 多步记录
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ToolStep:
    """多步执行中的单步定义"""
    tool_name: str
    params: Dict[str, Any]
    description: str = ""
    depends_on: Optional[str] = None  # 依赖前一步的tool_name

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.agent_id = f'agent-{name}-{uuid.uuid4().hex[:8]}'
        self.name = name
        self.description = description
        self._tools: Dict[str, Callable] = {}
        self._memory: List[AgentResult] = []
        self.conversation_memory = ConversationMemory()  # P0-C.3-2

    def register_tool(self, name: str, func: Callable):
        self._tools[name] = func

    def get_tools(self) -> Dict[str, Callable]:
        return self._tools

    async def use_tool(self, name: str, **kwargs) -> Any:
        """单Tool调用（保留向后兼容）"""
        if name not in self._tools:
            raise ValueError(f'Tool {name} not registered')
        result = await self._tools[name](**kwargs)
        self.conversation_memory.record(name, result, source="tool")
        return result

    async def execute_chain(self, ctx: AgentContext, steps: List[ToolStep]) -> AgentResult:
        """
        P0-C.3-2: 多步执行链 — 按顺序执行多个Tool，前一步输出可传递给后一步。

        Args:
            ctx: 当前Agent上下文
            steps: 按顺序执行的Tool步骤定义

        Returns:
            AgentResult with chain_steps记录每一步结果
        """
        chain_results = []
        tool_calls = []
        previous_output = None

        for step in steps:
            params = dict(step.params)

            # 如果依赖前一步，把前一步的输出注入
            if step.depends_on and previous_output is not None:
                params["previous_result"] = previous_output

            # 注入当前记忆上下文
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

                # 如果某步失败且是关键步骤，提前终止
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

        # 编译最终结果
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
        """编译链式执行的高级摘要"""
        steps_done = [r["step"] for r in chain_results if r.get("success")]
        if not steps_done:
            return "No steps completed."
        return f"Chain completed {len(steps_done)} steps: {' → '.join(steps_done)}"

    async def execute(self, ctx: AgentContext) -> AgentResult:
        """
        单步执行（子类可覆盖）。
        默认行为：使用 execute_chain 执行单一 ToolStep。
        """
        return await self.execute_chain(ctx, [])

    def remember(self, result: AgentResult):
        self._memory.append(result)
        if len(self._memory) > 100:
            self._memory = self._memory[-50:]

    def get_memory(self, limit: int = 10) -> List[AgentResult]:
        return self._memory[-limit:]

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.name})>'
