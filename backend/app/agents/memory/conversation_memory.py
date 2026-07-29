"""
GEO-Industry-Engine Agent Memory Module
P0-C.3-2: Agent多步链路 — 短期记忆 + 长期记忆

短期记忆: 运行时 in-memory (当前会话上下文 + 工具调用链)
长期记忆: PostgreSQL 持久化 (跨会话知识积累)
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import json


@dataclass
class MemoryEntry:
    """单条记忆条目"""
    key: str
    value: Any
    source: str = "agent"       # agent / tool / user / system
    step: int = 0               # 执行步骤编号
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl: int = 3600             # 秒, 0=永久
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.ttl == 0:
            return False
        return (datetime.now(timezone.utc) - self.timestamp).total_seconds() > self.ttl


class ConversationMemory:
    """
    Agent多步执行记忆系统。

    使用模式:
        mem = ConversationMemory(max_entries=100)
        mem.record("context", {"company_id": "xxx"}, source="tool", step=1)
        ctx = mem.get_context()  # 获取当前链式上下文
        mem.snapshot()           # 持久化快照
    """

    def __init__(self, max_entries: int = 200):
        self._entries: List[MemoryEntry] = []
        self.max_entries = max_entries
        self._step_counter = 0

    def record(self, key: str, value: Any, source: str = "agent",
               step: Optional[int] = None, ttl: int = 3600,
               metadata: Optional[Dict] = None):
        """记录一条记忆。自动递增步骤。"""
        if step is None:
            self._step_counter += 1
            step = self._step_counter

        entry = MemoryEntry(
            key=key,
            value=value,
            source=source,
            step=step,
            ttl=ttl,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        self._prune()

    def get(self, key: str, default: Any = None) -> Any:
        """按key获取最新值。"""
        for entry in reversed(self._entries):
            if entry.key == key and not entry.is_expired():
                return entry.value
        return default

    def get_context(self, max_steps: int = 10) -> Dict[str, Any]:
        """获取当前链式上下文，供下一步Tool使用。"""
        valid = [e for e in self._entries if not e.is_expired()]
        recent = valid[-max_steps:] if len(valid) > max_steps else valid
        return {
            "steps": {e.step: {"key": e.key, "value": e.value, "source": e.source}
                      for e in recent},
            "last_step": max([e.step for e in recent]) if recent else 0,
            "last_result": recent[-1].value if recent else None,
            "tool_chain": [e.key for e in recent if e.source == "tool"],
        }

    def get_tool_results(self) -> List[Dict]:
        """获取所有Tool调用的结果，供编译阶段使用。"""
        return [
            {"step": e.step, "tool": e.key, "result": e.value, "ts": e.timestamp.isoformat()}
            for e in self._entries if e.source == "tool" and not e.is_expired()
        ]

    def snapshot(self) -> Dict[str, Any]:
        """生成可序列化的快照（供持久化到DB）。"""
        valid = [e for e in self._entries if not e.is_expired()]
        return {
            "total_entries": len(valid),
            "steps": self._step_counter,
            "entries": [
                {
                    "key": e.key, "value": e.value, "source": e.source,
                    "step": e.step, "ts": e.timestamp.isoformat()
                }
                for e in valid[-50:]  # 仅保留最近50条
            ],
        }

    def clear(self):
        """清空当前会话记忆。"""
        self._entries.clear()
        self._step_counter = 0

    def _prune(self):
        """超过最大条目时裁剪旧记录。"""
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries // 2:]

