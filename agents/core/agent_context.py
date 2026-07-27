from typing import Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentContext:
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    history: List[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_event(self, event_type: str, data: Any):
        self.history.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def summary(self) -> dict:
        return {
            "query": self.query,
            "user_id": self.user_id,
            "steps": len(self.history),
            "created_at": self.created_at.isoformat(),
        }
