# GEO Universe Event Store
# Append-only event log with time-travel replay capability.
# All state changes in the Universe are recorded as immutable events.

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
from functools import lru_cache


@dataclass
class UniverseEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    node_id: Optional[str] = None
    node_type: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actor: str = "system"
    version: int = 1


class EventStore:
    _instance = None

    def __init__(self):
        self._events: List[UniverseEvent] = []
        self._by_node: Dict[str, List[UniverseEvent]] = {}
        self._by_type: Dict[str, List[UniverseEvent]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        if cls._instance:
            cls._instance._events.clear()
            cls._instance._by_node.clear()
            cls._instance._by_type.clear()
        cls._instance = None

    def append(self, event: UniverseEvent) -> UniverseEvent:
        self._events.append(event)
        if event.node_id:
            self._by_node.setdefault(event.node_id, []).append(event)
        self._by_type.setdefault(event.event_type, []).append(event)
        return event

    def append_batch(self, events: List[UniverseEvent]) -> List[UniverseEvent]:
        return [self.append(e) for e in events]

    def get_all(self, limit: int = 1000, offset: int = 0):
        return self._events[offset:offset + limit]

    def get_by_node(self, node_id: str):
        return self._by_node.get(node_id, [])

    def get_by_type(self, event_type: str):
        return self._by_type.get(event_type, [])

    def get_by_time_range(self, start: str, end: str):
        return [e for e in self._events if start <= e.timestamp <= end]

    def get_since(self, timestamp: str):
        return [e for e in self._events if e.timestamp >= timestamp]

    def replay_until(self, at_timestamp: str) -> Dict[str, Any]:
        state = {"nodes": {}, "relationships": [], "evidence": [], "scores": {}, "snapshot_at": at_timestamp}
        for e in self._events:
            if e.timestamp > at_timestamp:
                break
            self._apply_to_state(state, e)
        return state

    def _apply_to_state(self, state: Dict, event: UniverseEvent):
        p = event.payload
        if event.event_type == "node_created":
            state["nodes"][p.get("node_id", event.node_id)] = p
        elif event.event_type == "node_updated":
            nid = p.get("node_id", event.node_id)
            if nid in state["nodes"]:
                state["nodes"][nid].update(p.get("changes", {}))
        elif event.event_type == "relationship_added":
            state["relationships"].append(p)
        elif event.event_type == "evidence_added":
            state["evidence"].append(p)
        elif event.event_type == "score_changed":
            nid = p.get("node_id", event.node_id)
            state["scores"][nid] = p.get("new_score", 0)

    def stats(self) -> Dict[str, Any]:
        return {
            "total_events": len(self._events),
            "event_types": list(self._by_type.keys()),
            "affected_nodes": len(self._by_node),
            "date_range": {
                "first": self._events[0].timestamp if self._events else None,
                "last": self._events[-1].timestamp if self._events else None,
            },
        }


@lru_cache()
def get_event_store() -> EventStore:
    return EventStore.get_instance()
