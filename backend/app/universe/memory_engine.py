# GEO Universe Memory Engine
# Capability 2: Memory ? remember the past.
#
# 4-layer memory architecture:
#   Facts    ? atomic observations ("got certified")
#   Evidence ? verifiable proof backing each fact
#   Events   ? time-ordered sequences of related facts
#   Stories  ? AI-generated narrative interpretations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from functools import lru_cache
import uuid


@dataclass
class Fact:
    """Layer 1: An atomic, verifiable statement about a node."""
    fact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str = ""
    node_type: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    category: str = ""              # certification, relationship, growth, capability, score
    statement: str = ""             # "Obtained GEO Certification Level 3"
    source: str = "system"
    confidence: float = 1.0
    valid_from: str = ""
    valid_until: str = ""
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "category": self.category,
            "statement": self.statement,
            "source": self.source,
            "confidence": self.confidence,
            "valid_from": self.valid_from, "valid_until": self.valid_until,
        }


@dataclass
class Evidence:
    """Layer 2: Verifiable proof that backs a Fact."""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fact_id: str = ""
    evidence_type: str = ""         # certificate, url, screenshot, audit, tx_hash
    uri: str = ""                   # link or reference to the evidence
    verified: bool = False
    verified_by: str = ""
    verified_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    validity_period_days: int = 365
    expires_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "fact_id": self.fact_id,
            "evidence_type": self.evidence_type,
            "uri": self.uri,
            "verified": self.verified,
        }


@dataclass
class MemoryEvent:
    """Layer 3: A time-ordered event composed of related Facts."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    node_id: str = ""
    node_type: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    facts: List[str] = field(default_factory=list)         # fact_ids
    evidence: List[str] = field(default_factory=list)       # evidence_ids
    impact: Dict[str, Any] = field(default_factory=dict)    # before/after snapshots
    significance: float = 0.0
    lifecycle_stage: str = "active"     # active | superseded | archived
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "timestamp": self.timestamp,
            "fact_count": len(self.facts),
            "significance": self.significance,
        }


@dataclass
class Story:
    """Layer 4: A narrative interpretation of events over time."""
    story_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str = ""
    title: str = ""
    narrative: str = ""
    period_start: str = ""
    period_end: str = ""
    events: List[str] = field(default_factory=list)         # event_ids
    themes: List[str] = field(default_factory=list)
    generated_by: str = "system"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "story_id": self.story_id,
            "title": self.title,
            "narrative": self.narrative,
            "period": f"{self.period_start} -> {self.period_end}",
            "event_count": len(self.events),
            "themes": self.themes,
        }


class MemoryEngine:
    """Manages the 4-layer memory for all Universe nodes.

    Facts feed into Events, which feed into Stories.
    Every layer is backed by verifiable Evidence.

    Usage:
        engine = MemoryEngine.get_instance()
        fact = engine.record_fact(node_id="...", statement="...")
        event = engine.create_event_from_facts(node_id="...", fact_ids=[...])
        story = engine.generate_story(node_id="...", title="...")
    """

    _instance: Optional["MemoryEngine"] = None

    def __init__(self):
        self._facts: Dict[str, Fact] = {}
        self._evidence: Dict[str, Evidence] = {}
        self._events: Dict[str, MemoryEvent] = {}
        self._stories: Dict[str, Story] = {}
        self._by_node: Dict[str, List[str]] = {}   # node_id -> [fact_ids]

    @classmethod
    def get_instance(cls) -> "MemoryEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Layer 1: Facts ----

    def record_fact(self, node_id: str, node_type: str, statement: str,
                    category: str = "general", source: str = "system",
                    confidence: float = 1.0) -> Fact:
        """Record a single atomic fact about a node."""
        fact = Fact(
            node_id=node_id,
            node_type=node_type,
            statement=statement,
            category=category,
            source=source,
            confidence=confidence,
        )
        self._facts[fact.fact_id] = fact
        self._by_node.setdefault(node_id, []).append(fact.fact_id)
        return fact

    def record_facts_batch(self, facts_data: List[Dict]) -> List[Fact]:
        """Record multiple facts at once."""
        return [self.record_fact(**fd) for fd in facts_data]

    def get_facts(self, node_id: str = None, category: str = None) -> List[Fact]:
        """Query facts by node and/or category."""
        facts = list(self._facts.values())
        if node_id:
            fact_ids = self._by_node.get(node_id, [])
            facts = [self._facts[fid] for fid in fact_ids if fid in self._facts]
        if category:
            facts = [f for f in facts if f.category == category]
        return sorted(facts, key=lambda f: f.timestamp, reverse=True)

    # ---- Layer 2: Evidence ----

    def attach_evidence(self, fact_id: str, evidence_type: str, uri: str,
                        metadata: Dict = None) -> Optional[Evidence]:
        """Attach verifiable evidence to a fact."""
        if fact_id not in self._facts:
            return None
        ev = Evidence(
            fact_id=fact_id,
            evidence_type=evidence_type,
            uri=uri,
            metadata=metadata or {},
        )
        self._evidence[ev.evidence_id] = ev
        return ev

    def verify_evidence(self, evidence_id: str, verified_by: str) -> bool:
        """Mark an evidence record as verified."""
        ev = self._evidence.get(evidence_id)
        if not ev:
            return False
        ev.verified = True
        ev.verified_by = verified_by
        ev.verified_at = datetime.now(timezone.utc).isoformat()
        return True

    def get_evidence_for_fact(self, fact_id: str) -> List[Evidence]:
        return [e for e in self._evidence.values() if e.fact_id == fact_id]

    # ---- Layer 3: Events ----

    def create_event(self, title: str, description: str, node_id: str,
                     node_type: str, fact_ids: List[str],
                     impact: Dict = None) -> MemoryEvent:
        """Create a time-ordered event from one or more facts."""
        # Gather evidence for all facts
        evidence_ids = []
        for fid in fact_ids:
            for ev in self.get_evidence_for_fact(fid):
                evidence_ids.append(ev.evidence_id)

        # Calculate significance
        significance = min(len(fact_ids) * 0.1 + len(evidence_ids) * 0.05, 1.0)

        event = MemoryEvent(
            title=title,
            description=description,
            node_id=node_id,
            node_type=node_type,
            facts=fact_ids,
            evidence=evidence_ids,
            impact=impact or {},
            significance=significance,
        )
        self._events[event.event_id] = event
        return event

    def get_events(self, node_id: str = None, min_significance: float = 0.0) -> List[MemoryEvent]:
        events = list(self._events.values())
        if node_id:
            events = [e for e in events if e.node_id == node_id]
        if min_significance > 0:
            events = [e for e in events if e.significance >= min_significance]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    # ---- Layer 4: Stories ----

    def generate_story(self, node_id: str, title: str = "",
                       period_start: str = "", period_end: str = "",
                       themes: List[str] = None) -> Story:
        """Generate a narrative story from a node's events.

        In production, this would use an AI Provider to generate the narrative.
        For now, it constructs a structured story from events and facts.
        """
        events = self.get_events(node_id)
        if not events:
            return Story(node_id=node_id, title=title or "No events yet",
                        narrative="This node has no recorded events to tell a story about.")

        # Build narrative from events
        event_summaries = []
        for e in events:
            facts = [self._facts[fid].statement for fid in e.facts if fid in self._facts]
            event_summaries.append(f"[{e.timestamp[:10]}] {e.title}: {', '.join(facts[:3])}")

        if not period_start and events:
            period_start = events[-1].timestamp[:10] if events else ""
        if not period_end and events:
            period_end = events[0].timestamp[:10] if events else ""

        narrative_parts = [f"Over the period {period_start} to {period_end}, this node experienced {len(events)} significant events:"]
        narrative_parts.extend(event_summaries[:10])

        # Determine themes
        auto_themes = []
        categories = set()
        for e in events:
            for fid in e.facts:
                if fid in self._facts:
                    categories.add(self._facts[fid].category)
        if "certification" in categories:
            auto_themes.append("Building Trust")
        if "growth" in categories:
            auto_themes.append("Growth Journey")
        if "relationship" in categories:
            auto_themes.append("Expanding Network")
        if "capability" in categories:
            auto_themes.append("Capability Development")

        story = Story(
            node_id=node_id,
            title=title or f"Memory of {node_id[:8]}",
            narrative="\n".join(narrative_parts),
            period_start=period_start,
            period_end=period_end,
            events=[e.event_id for e in events[:20]],
            themes=themes or auto_themes,
        )
        self._stories[story.story_id] = story
        return story

    def get_stories(self, node_id: str = None) -> List[Story]:
        stories = list(self._stories.values())
        if node_id:
            stories = [s for s in stories if s.node_id == node_id]
        return sorted(stories, key=lambda s: s.generated_at, reverse=True)

    # ---- Cross-layer timeline ----

    def get_timeline(self, node_id: str) -> Dict[str, Any]:
        """Get the full 4-layer memory timeline for a node."""
        facts = self.get_facts(node_id)
        events = self.get_events(node_id)
        stories = self.get_stories(node_id)

        return {
            "node_id": node_id,
            "layers": {
                "facts": {"count": len(facts), "items": [f.to_dict() for f in facts[:50]]},
                "evidence": {"count": len(self._evidence), "verified": sum(1 for e in self._evidence.values() if e.verified)},
                "events": {"count": len(events), "items": [e.to_dict() for e in events[:20]]},
                "stories": {"count": len(stories), "items": [s.to_dict() for s in stories[:5]]},
            },
            "significant_events": [
                {"title": e.title, "date": e.timestamp[:10], "significance": e.significance}
                for e in sorted(events, key=lambda x: x.significance, reverse=True)[:5]
            ],
        }


    # ---- Temporal Queries ----

    def get_timeline_snapshot(self, node_id: str, at_timestamp: str) -> Dict[str, Any]:
        """Get the memory state as it existed at a specific timestamp."""
        facts = [f for f in self.get_facts(node_id) if f.timestamp <= at_timestamp]
        events = [e for e in self.get_events(node_id) if e.timestamp <= at_timestamp]
        return {
            "snapshot_at": at_timestamp,
            "facts_count": len(facts),
            "events_count": len(events),
            "facts": [f.to_dict() for f in facts[:20]],
            "events": [e.to_dict() for e in events[:10]],
        }

    def get_valid_evidence(self, fact_id: str) -> List[Evidence]:
        """Get only evidence that has not expired."""
        now = datetime.now(timezone.utc).isoformat()
        return [e for e in self.get_evidence_for_fact(fact_id)
                if not e.expires_at or e.expires_at > now]

    def get_growth_velocity(self, node_id: str) -> Dict[str, Any]:
        """Calculate how fast a node is growing based on fact density over time."""
        facts = self.get_facts(node_id)
        if len(facts) < 2:
            return {"velocity": 0, "trend": "unknown", "message": "Insufficient data"}

        timestamps = sorted([f.timestamp for f in facts])
        first = timestamps[0]
        last = timestamps[-1]
        days = max(1, (datetime.fromisoformat(last) - datetime.fromisoformat(first)).days)
        facts_per_month = len(facts) / max(days / 30, 1)

        # Compare recent velocity (last 90 days) vs overall
        cutoff = (datetime.fromisoformat(last) - timedelta(days=90)).isoformat()
        recent = [f for f in facts if f.timestamp >= cutoff]
        recent_velocity = len(recent) / 3  # per month

        trend = "accelerating" if recent_velocity > facts_per_month * 1.2 else \
                "decelerating" if recent_velocity < facts_per_month * 0.8 else "stable"

        return {
            "velocity": round(facts_per_month, 2),
            "recent_velocity": round(recent_velocity, 2),
            "total_facts": len(facts),
            "recent_facts": len(recent),
            "trend": trend,
            "period_days": days,
        }

    # ---- Stats ----


    def stats(self) -> Dict[str, Any]:
        return {
            "total_facts": len(self._facts),
            "total_evidence": len(self._evidence),
            "total_events": len(self._events),
            "total_stories": len(self._stories),
            "nodes_with_memory": len(self._by_node),
            "fact_categories": list(set(f.category for f in self._facts.values())),
        }

    def export_full(self) -> Dict[str, Any]:
        return {
            "stats": self.stats(),
            "by_node": {nid: len(fids) for nid, fids in self._by_node.items()},
        }


@lru_cache()
def get_memory_engine() -> MemoryEngine:
    return MemoryEngine.get_instance()
