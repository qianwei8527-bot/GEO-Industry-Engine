"""C6.6.6 Event Backbone — minimal unified event skeleton.

A UniverseEvent is the fact layer. Domain events (ReputationEvent,
RelationshipEvent, GeoEvent) remain untouched; the backbone indexes them
under a common structure and lets the Law Engine react.

Prototype scope: certification / reputation / relationship events only.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from functools import lru_cache
import uuid


@dataclass
class UniverseEvent:
    event_id: str = ""
    node_id: str = ""
    related_node_ids: List[str] = field(default_factory=list)
    domain: str = ""                 # reputation | relationship | observation | transaction | memory | governance
    event_type: str = ""             # domain native type (e.g. certification_passed)
    occurred_at: str = ""
    actor_id: str = "system"
    source: str = "system"
    rule_ids: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""

    def __post_init__(self):
        if not self.event_id: self.event_id = str(uuid.uuid4())
        if not self.occurred_at: self.occurred_at = datetime.now(timezone.utc).isoformat()
        if not self.correlation_id: self.correlation_id = str(uuid.uuid4())

    def to_dict(self):
        return {"event_id": self.event_id, "node_id": self.node_id,
                "related_node_ids": self.related_node_ids, "domain": self.domain,
                "event_type": self.event_type, "occurred_at": self.occurred_at,
                "actor_id": self.actor_id, "source": self.source,
                "rule_ids": self.rule_ids, "payload": self.payload,
                "correlation_id": self.correlation_id}


class EventBackbone:
    _instance = None
    _events: List[UniverseEvent] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    def emit(self, event: UniverseEvent) -> UniverseEvent:
        self._events.append(event)
        # Prototype: index node + type; Law Engine is invoked by the caller to keep causality explicit.
        return event

    def timeline(self, node_id: str = None, limit: int = 100) -> List[Dict]:
        evs = self._events
        if node_id:
            evs = [e for e in evs if e.node_id == node_id or node_id in e.related_node_ids]
        return [e.to_dict() for e in evs[-limit:]]

    def clear(self):
        self._events.clear()

    @classmethod
    def reset(cls):
        cls._instance = None
        cls._events = []


@lru_cache()
def get_event_backbone():
    return EventBackbone.get_instance()
