# GEO Universe Opportunity Memory Engine
# Phase C5.4 — Universe Relationship Learning Loop.
#
# C5.3 answers "WHY should this connection happen?"
# C5.4 answers "What happened last time we recommended this, and what did we learn?"
#
# This is the memory layer that transforms Universe from a one-shot
# analysis machine into a learning system. It tracks:
#   - Opportunity lifecycle (created -> accepted/rejected -> succeeded/failed)
#   - Outcome measurement (business value, relationship growth, reputation change)
#   - Learning adjustment (using past outcomes to improve future confidence)
#
# Principle: Universe shows possibilities. Users decide. Outcomes teach Universe.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from functools import lru_cache
import uuid
import math

print("Phase C5.4: Opportunity Memory Engine loaded")

# ========== Connection Value Vector ==========

@dataclass
class ConnectionValueVector:
    revenue: float = 0.0
    capability: float = 0.0
    reputation: float = 0.0
    knowledge: float = 0.0
    network: float = 0.0
    overall: float = 0.0

    def __post_init__(self):
        self.overall = round(sum([
            self.revenue, self.capability, self.reputation, self.knowledge, self.network
        ]) / 5.0, 2)

    def to_dict(self):
        return {
            "revenue": round(self.revenue, 2),
            "capability": round(self.capability, 2),
            "reputation": round(self.reputation, 2),
            "knowledge": round(self.knowledge, 2),
            "network": round(self.network, 2),
            "overall": self.overall,
        }

    @classmethod
    def from_expected_value(cls, ev):
        cap = ev.get("capability_gain", 0)
        growth = ev.get("growth_acceleration", 0)
        strategic = ev.get("strategic_value", 0)
        return cls(
            revenue=growth * 0.7,
            capability=cap,
            reputation=strategic * 0.3,
            knowledge=cap * 0.5 + strategic * 0.2,
            network=strategic * 0.5,
        )


# ========== Opportunity Event ==========

@dataclass
class RelationshipOpportunityEvent:
    event_id: str = ""
    opportunity_id: str = ""
    node_a_id: str = ""
    node_b_id: str = ""
    event_type: str = ""
    reason: str = ""
    confidence_before: float = 0.0
    details: Dict = field(default_factory=dict)
    actor_id: str = ""
    timestamp: str = ""

    VALID_TYPES = {
        "opportunity_created", "opportunity_viewed",
        "accepted", "rejected",
        "relationship_created", "relationship_failed_to_create",
        "collaboration_started", "collaboration_completed",
        "successful", "failed", "stalled",
    }

    def __post_init__(self):
        if not self.event_id: self.event_id = str(uuid.uuid4())[:8]
        if not self.timestamp: self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.event_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid event_type: {self.event_type}. Must be one of {self.VALID_TYPES}")

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "opportunity_id": self.opportunity_id,
            "node_a_id": self.node_a_id, "node_b_id": self.node_b_id,
            "event_type": self.event_type,
            "reason": self.reason,
            "confidence_before": round(self.confidence_before, 2),
            "details": self.details,
            "actor_id": self.actor_id,
            "timestamp": self.timestamp,
        }


# ========== Opportunity Outcome ==========

@dataclass
class OpportunityOutcome:
    outcome_id: str = ""
    opportunity_id: str = ""
    node_a_id: str = ""
    node_b_id: str = ""
    status: str = ""
    value_realized: ConnectionValueVector = field(default_factory=ConnectionValueVector)
    relationship_growth: str = ""
    reputation_change_a: float = 0.0
    reputation_change_b: float = 0.0
    business_metrics: Dict = field(default_factory=dict)
    notes: str = ""
    recorded_at: str = ""

    VALID_STATUSES = {"pending", "in_progress", "successful", "failed", "stalled", "cancelled"}

    def __post_init__(self):
        if not self.outcome_id: self.outcome_id = str(uuid.uuid4())[:8]
        if not self.recorded_at: self.recorded_at = datetime.now(timezone.utc).isoformat()
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")

    def to_dict(self):
        return {
            "outcome_id": self.outcome_id,
            "opportunity_id": self.opportunity_id,
            "node_a_id": self.node_a_id, "node_b_id": self.node_b_id,
            "status": self.status,
            "value_realized": self.value_realized.to_dict(),
            "relationship_growth": self.relationship_growth,
            "reputation_change_a": round(self.reputation_change_a, 2),
            "reputation_change_b": round(self.reputation_change_b, 2),
            "business_metrics": self.business_metrics,
            "notes": self.notes,
            "recorded_at": self.recorded_at,
        }

# ========== Opportunity Memory Store ==========

class OpportunityMemoryStore:
    _instance = None

    def __init__(self):
        self._events: Dict[str, List[RelationshipOpportunityEvent]] = {}
        self._outcomes: Dict[str, OpportunityOutcome] = {}
        self._opportunity_history: Dict[str, List[str]] = {}
        self._node_events: Dict[str, List[str]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    def append_event(self, event: RelationshipOpportunityEvent):
        oid = event.opportunity_id
        self._events.setdefault(oid, []).append(event)
        self._opportunity_history.setdefault(oid, [])
        self._opportunity_history[oid].append(event.event_id)
        for nid in (event.node_a_id, event.node_b_id):
            self._node_events.setdefault(nid, [])
            self._node_events[nid].append(event.event_id)
        return event

    def record_outcome(self, outcome: OpportunityOutcome):
        self._outcomes[outcome.opportunity_id] = outcome
        return outcome

    def get_events(self, opportunity_id: str) -> List[RelationshipOpportunityEvent]:
        return self._events.get(opportunity_id, [])

    def get_lifecycle(self, opportunity_id: str) -> List[Dict]:
        events = self.get_events(opportunity_id)
        return [
            {"event_type": e.event_type, "timestamp": e.timestamp,
             "reason": e.reason, "confidence_before": e.confidence_before}
            for e in sorted(events, key=lambda x: x.timestamp)
        ]

    def get_outcome(self, opportunity_id: str) -> Optional[OpportunityOutcome]:
        return self._outcomes.get(opportunity_id)

    def get_node_history(self, node_id: str) -> List[Dict]:
        event_ids = self._node_events.get(node_id, [])
        results = []
        seen = set()
        for eid in event_ids:
            for oid, events in self._events.items():
                for e in events:
                    if e.event_id == eid and eid not in seen:
                        seen.add(eid)
                        results.append(e.to_dict())
        return sorted(results, key=lambda x: x.get("timestamp", ""))

    def get_success_rate(self, node_id: str = None, node_type: str = None) -> float:
        outcomes = list(self._outcomes.values())
        if not outcomes:
            return 0.5
        successful = sum(1 for o in outcomes if o.status == "successful")
        total = len(outcomes)
        return successful / total if total > 0 else 0.5

    def get_accepted_rate(self, node_id: str = None) -> float:
        accepted = 0
        total = 0
        for events in self._events.values():
            for e in events:
                if e.event_type == "accepted":
                    accepted += 1
                    total += 1
                elif e.event_type == "rejected":
                    total += 1
        return accepted / total if total > 0 else 0.5

    @classmethod
    def reset(cls):
        cls._instance = None


# ========== Learning Adjustment ==========

class LearningAdjustment:
    def __init__(self):
        self.store = OpportunityMemoryStore.get_instance()
        self.learning_rate = 0.1
        self.min_adjustment = -0.15
        self.max_adjustment = 0.15

    def adjust_confidence(self, opportunity_id: str, base_confidence: float) -> float:
        events = self.store.get_events(opportunity_id)
        if not events:
            return base_confidence
        creation_event = None
        for e in events:
            if e.event_type == "opportunity_created":
                creation_event = e
                break
        if not creation_event:
            return base_confidence
        node_a = creation_event.node_a_id
        node_b = creation_event.node_b_id
        node_pair_outcomes = self._get_pair_outcomes(node_a, node_b)
        if not node_pair_outcomes:
            outcome = self.store.get_outcome(opportunity_id)
            if outcome:
                return self._adjust_from_outcome(base_confidence, outcome)
            return base_confidence
        success_count = sum(1 for o in node_pair_outcomes if o.status == "successful")
        fail_count = sum(1 for o in node_pair_outcomes if o.status == "failed")
        total = len(node_pair_outcomes)
        if total == 0:
            return base_confidence
        success_rate = success_count / total
        if success_rate >= 0.8:
            adjustment = self.learning_rate
        elif success_rate >= 0.5:
            adjustment = 0.0
        elif success_rate > 0.0:
            adjustment = -self.learning_rate * (1 - success_rate)
        else:
            adjustment = -self.max_adjustment
        adjustment = max(self.min_adjustment, min(self.max_adjustment, adjustment))
        return round(max(0.0, min(1.0, base_confidence + adjustment)), 2)

    def get_node_learning_stats(self, node_id: str) -> Dict:
        event_ids = self.store._node_events.get(node_id, [])
        stats = {"total_opportunities": 0, "accepted": 0, "rejected": 0,
                 "successful": 0, "failed": 0, "success_rate": 0.0,
                 "accept_rate": 0.0, "average_confidence": 0.0}
        seen = set()
        confidences = []
        for eid in event_ids:
            for oid, events in self.store._events.items():
                for e in events:
                    if e.event_id == eid and eid not in seen:
                        seen.add(eid)
                        stats["total_opportunities"] += 1
                        if e.event_type == "accepted": stats["accepted"] += 1
                        if e.event_type == "rejected": stats["rejected"] += 1
                        confidences.append(e.confidence_before)
        for outcome in self.store._outcomes.values():
            if outcome.status == "successful": stats["successful"] += 1
            if outcome.status == "failed": stats["failed"] += 1
        total_decisions = stats["accepted"] + stats["rejected"]
        stats["accept_rate"] = round(stats["accepted"] / total_decisions, 2) if total_decisions > 0 else 0.0
        total_outcomes = stats["successful"] + stats["failed"]
        stats["success_rate"] = round(stats["successful"] / total_outcomes, 2) if total_outcomes > 0 else 0.0
        stats["average_confidence"] = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
        return stats

    def _get_pair_outcomes(self, node_a_id: str, node_b_id: str) -> List[OpportunityOutcome]:
        results = []
        for outcome in self.store._outcomes.values():
            if (outcome.node_a_id == node_a_id and outcome.node_b_id == node_b_id) or                (outcome.node_a_id == node_b_id and outcome.node_b_id == node_a_id):
                results.append(outcome)
        return results

    def _adjust_from_outcome(self, base: float, outcome: OpportunityOutcome) -> float:
        if outcome.status == "successful":
            return round(min(1.0, base + self.learning_rate * 0.5), 2)
        elif outcome.status == "failed":
            return round(max(0.0, base - self.learning_rate), 2)
        return base

    @classmethod
    def reset(cls):
        cls._instance = None


# ========== Opportunity Memory Engine ==========

class OpportunityMemoryEngine:
    _instance = None

    def __init__(self):
        self.store = OpportunityMemoryStore.get_instance()
        self.learning = LearningAdjustment()

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    def record_created(self, opportunity_id: str, node_a_id: str, node_b_id: str,
                       confidence: float = 0.0, reason: str = "", details: Dict = None):
        return self.store.append_event(RelationshipOpportunityEvent(
            opportunity_id=opportunity_id, node_a_id=node_a_id, node_b_id=node_b_id,
            event_type="opportunity_created", confidence_before=confidence,
            reason=reason, details=details or {}))

    def record_accepted(self, opportunity_id: str, actor_id: str = "", reason: str = ""):
        events = self.store.get_events(opportunity_id)
        last_conf = events[-1].confidence_before if events else 0.0
        return self.store.append_event(RelationshipOpportunityEvent(
            opportunity_id=opportunity_id,
            node_a_id=events[0].node_a_id if events else "",
            node_b_id=events[0].node_b_id if events else "",
            event_type="accepted", confidence_before=last_conf,
            reason=reason, actor_id=actor_id))

    def record_rejected(self, opportunity_id: str, actor_id: str = "", reason: str = ""):
        events = self.store.get_events(opportunity_id)
        last_conf = events[-1].confidence_before if events else 0.0
        return self.store.append_event(RelationshipOpportunityEvent(
            opportunity_id=opportunity_id,
            node_a_id=events[0].node_a_id if events else "",
            node_b_id=events[0].node_b_id if events else "",
            event_type="rejected", confidence_before=last_conf,
            reason=reason, actor_id=actor_id))

    def record_outcome(self, opportunity_id: str, status: str,
                       value_realized: ConnectionValueVector = None,
                       relationship_growth: str = "",
                       reputation_change_a: float = 0.0,
                       reputation_change_b: float = 0.0,
                       notes: str = ""):
        events = self.store.get_events(opportunity_id)
        if not events:
            raise ValueError(f"No events for opportunity: {opportunity_id}")
        first_event = events[0]
        outcome = OpportunityOutcome(
            opportunity_id=opportunity_id,
            node_a_id=first_event.node_a_id,
            node_b_id=first_event.node_b_id,
            status=status,
            value_realized=value_realized or ConnectionValueVector(),
            relationship_growth=relationship_growth,
            reputation_change_a=reputation_change_a,
            reputation_change_b=reputation_change_b,
            notes=notes,
        )
        self.store.record_outcome(outcome)
        if status in ("successful", "failed"):
            event_type = "successful" if status == "successful" else "failed"
            self.store.append_event(RelationshipOpportunityEvent(
                opportunity_id=opportunity_id,
                node_a_id=first_event.node_a_id,
                node_b_id=first_event.node_b_id,
                event_type=event_type,
                confidence_before=events[-1].confidence_before if events else 0.0,
                reason=notes,
            ))
        return outcome

    def get_adjusted_confidence(self, opportunity_id: str, base_confidence: float) -> float:
        return self.learning.adjust_confidence(opportunity_id, base_confidence)

    def get_lifecycle(self, opportunity_id: str) -> List[Dict]:
        return self.store.get_lifecycle(opportunity_id)

    def get_outcome(self, opportunity_id: str) -> Optional[Dict]:
        outcome = self.store.get_outcome(opportunity_id)
        return outcome.to_dict() if outcome else None

    def get_node_stats(self, node_id: str) -> Dict:
        return self.learning.get_node_learning_stats(node_id)

    def get_success_rate(self, node_id: str = None) -> float:
        return self.store.get_success_rate(node_id)

    def seed_sample_data(self):
        oid1 = "opp-seed-001"
        oid2 = "opp-seed-002"
        self.record_created(oid1, "company-alpha", "company-beta", 0.72,
                           "High capability complementarity: Alpha lacks data, Beta provides it")
        self.record_accepted(oid1, "company-alpha", "Alpha needs data intelligence capability")
        self.record_outcome(oid1, "successful",
            ConnectionValueVector(revenue=0.35, capability=0.80, reputation=0.25, knowledge=0.40, network=0.30),
            relationship_growth="DISCOVERED->COLLABORATING",
            reputation_change_a=5.0, reputation_change_b=3.0,
            notes="Alpha acquired data capabilities through Beta. 3 projects completed.")
        self.record_created(oid2, "company-alpha", "provider-unknown", 0.45,
                           "Moderate alignment, unknown reputation")
        self.record_rejected(oid2, "company-alpha", "Insufficient reputation data for provider-unknown")
        stats_a = self.get_node_stats("company-alpha")
        return {
            "opportunities": [
                {"id": oid1, "lifecycle": self.get_lifecycle(oid1), "outcome": self.get_outcome(oid1)},
                {"id": oid2, "lifecycle": self.get_lifecycle(oid2), "outcome": None},
            ],
            "node_stats": stats_a,
            "success_rate": self.get_success_rate(),
        }

    @classmethod
    def reset(cls):
        cls._instance = None
        OpportunityMemoryStore.reset()


@lru_cache()
def get_opportunity_memory_engine() -> OpportunityMemoryEngine:
    return OpportunityMemoryEngine.get_instance()
