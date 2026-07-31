"""
GEO-Industry-Engine Agent Memory Module
P0-C.3-2 + P0-B: Agent multi-step memory with DB persistence.

Short-term: runtime in-memory (current session context + tool call chain)
Long-term: PostgreSQL persistence via AgentMemory model (cross-session knowledge)
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid


@dataclass
class MemoryEntry:
    """Single memory entry."""
    key: str
    value: Any
    source: str = "agent"
    step: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.ttl == 0:
            return False
        return (datetime.now(timezone.utc) - self.timestamp).total_seconds() > self.ttl


class ConversationMemory:
    """
    Agent multi-step execution memory with optional DB persistence.

    Usage:
        mem = ConversationMemory(max_entries=100)
        mem.session_id = "session-abc-123"
        mem.record("context", {"company_id": "xxx"}, source="tool", step=1)
        ctx = mem.get_context()
        await mem.persist_to_db(db_session)  # save to AgentMemory table
    """

    def __init__(self, max_entries: int = 200):
        self._entries: List[MemoryEntry] = []
        self.max_entries = max_entries
        self._step_counter = 0
        self.session_id: str = ""

    def new_session(self) -> str:
        """Start a new memory session."""
        self.session_id = f"session-{uuid.uuid4().hex[:16]}"
        self._entries.clear()
        self._step_counter = 0
        return self.session_id

    def record(self, key: str, value: Any, source: str = "agent",
               step: Optional[int] = None, ttl: int = 3600,
               metadata: Optional[Dict] = None):
        """Record a memory entry. Auto-increments step counter."""
        if step is None:
            self._step_counter += 1
            step = self._step_counter

        entry = MemoryEntry(
            key=key, value=value, source=source,
            step=step, ttl=ttl,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        self._prune()

    def get(self, key: str, default: Any = None) -> Any:
        """Get the latest value for a key."""
        for entry in reversed(self._entries):
            if entry.key == key and not entry.is_expired():
                return entry.value
        return default

    def get_context(self, max_steps: int = 10) -> Dict[str, Any]:
        """Get current chain context for next tool call."""
        valid = [e for e in self._entries if not e.is_expired()]
        recent = valid[-max_steps:] if len(valid) > max_steps else valid
        return {
            "steps": {
                e.step: {"key": e.key, "value": e.value, "source": e.source}
                for e in recent
            },
            "last_step": max([e.step for e in recent]) if recent else 0,
            "last_result": recent[-1].value if recent else None,
            "tool_chain": [e.key for e in recent if e.source == "tool"],
        }

    def get_tool_results(self) -> List[Dict]:
        """Get all tool call results for compilation."""
        return [
            {"step": e.step, "tool": e.key, "result": e.value, "ts": e.timestamp.isoformat()}
            for e in self._entries if e.source == "tool" and not e.is_expired()
        ]

    def snapshot(self) -> Dict[str, Any]:
        """Generate serializable snapshot for DB persistence."""
        valid = [e for e in self._entries if not e.is_expired()]
        return {
            "total_entries": len(valid),
            "steps": self._step_counter,
            "entries": [
                {
                    "key": e.key, "value": e.value, "source": e.source,
                    "step": e.step, "ts": e.timestamp.isoformat()
                }
                for e in valid[-50:]
            ],
        }

    async def persist_to_db(self, db, agent_name: str, task_id: str,
                            entity_id: Optional[str] = None,
                            summary: Optional[str] = None,
                            citations: Optional[Dict] = None) -> List[str]:
        """
        Persist current session memory to AgentMemory table.
        Returns list of created memory IDs.

        Args:
            db: AsyncSession
            agent_name: Name of the agent that produced this memory
            task_id: Unique task identifier
            entity_id: Optional associated entity UUID string
            summary: Optional human-readable summary
            citations: Optional citation data
        """
        from app.models.agent_memory import AgentMemory
        valid = [e for e in self._entries if not e.is_expired()]
        persisted_ids = []

        for entry in valid:
            mem = AgentMemory(
                agent_name=agent_name,
                session_id=self.session_id or "unknown",
                task_id=task_id,
                memory_type="tool_result" if entry.source == "tool" else "context",
                key=entry.key,
                value={"data": entry.value} if not isinstance(entry.value, (dict, list)) else entry.value,
                step_index=entry.step,
                entity_id=uuid.UUID(entity_id) if entity_id else None,
                metadata_json=entry.metadata,
            )
            db.add(mem)
            persisted_ids.append(str(mem.id))

        if summary or citations:
            summary_mem = AgentMemory(
                agent_name=agent_name,
                session_id=self.session_id or "unknown",
                task_id=task_id,
                memory_type="analysis",
                key="final_result",
                value=snapshot if (snapshot := self.snapshot()) else None,
                summary=summary,
                citations=citations,
                entity_id=uuid.UUID(entity_id) if entity_id else None,
            )
            db.add(summary_mem)
            persisted_ids.append(str(summary_mem.id))

        await db.commit()
        return persisted_ids

    @staticmethod
    async def load_from_db(db, session_id: str) -> Optional["ConversationMemory"]:
        """Load a previous session from DB into a new ConversationMemory."""
        from app.models.agent_memory import AgentMemory
        from sqlalchemy import select

        result = await db.execute(
            select(AgentMemory)
            .where(AgentMemory.session_id == session_id)
            .order_by(AgentMemory.step_index)
        )
        rows = result.scalars().all()

        if not rows:
            return None

        mem = ConversationMemory()
        mem.session_id = session_id
        for row in rows:
            mem.record(
                key=row.key,
                value=row.value.get("data") if isinstance(row.value, dict) and "data" in row.value else row.value,
                source="tool" if row.memory_type == "tool_result" else "agent",
                step=row.step_index or 0,
            )
        return mem

    def clear(self):
        """Clear current session memory."""
        self._entries.clear()
        self._step_counter = 0

    def _prune(self):
        """Prune old entries when exceeding max."""
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries // 2:]
