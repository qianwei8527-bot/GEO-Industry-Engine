# GEO Universe Transaction Engine
# Phase C6 — Transaction as the natural result of Connection.
#
# C5.3 answers "WHY should this connection happen?"
# C5.4 remembers "what happened with past opportunities?"
# C6 executes "the relationship becomes a delivered outcome."
#
# A transaction is NOT the first step. It is the final step of:
#   Position -> Need -> Capability -> Trust -> Relationship -> Transaction
#
# Every transaction is append-only, explainable, and feeds results back
# into Node Reputation, Relationship Reputation, Memory, and Future
# Possibility adjustment.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from functools import lru_cache
import uuid

from app.universe.opportunity_memory import ConnectionValueVector

print("Phase C6: Transaction Engine loaded")

# ========== Data Models ==========

@dataclass
class TransactionScope:
    category: str = "service"          # service | tool | data | knowledge | partnership
    title: str = ""
    description: str = ""
    budget_min: float = 0.0
    budget_max: float = 0.0
    currency: str = "CNY"
    timeline_days: int = 30
    deliverables: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "category": self.category, "title": self.title,
            "description": self.description,
            "budget_min": self.budget_min, "budget_max": self.budget_max,
            "currency": self.currency, "timeline_days": self.timeline_days,
            "deliverables": self.deliverables, "requirements": self.requirements,
        }


@dataclass
class TransactionEvent:
    event_id: str = ""
    transaction_id: str = ""
    event_type: str = ""
    actor_id: str = ""
    description: str = ""
    milestone_index: int = -1
    details: Dict = field(default_factory=dict)
    timestamp: str = ""

    VALID_TYPES = {
        "proposed", "agreed", "started", "milestone_completed",
        "delivered", "reviewed", "settled", "failed", "cancelled",
    }

    def __post_init__(self):
        if not self.event_id: self.event_id = str(uuid.uuid4())[:8]
        if not self.timestamp: self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.event_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid event_type: {self.event_type}")

    def to_dict(self):
        return {
            "event_id": self.event_id, "transaction_id": self.transaction_id,
            "event_type": self.event_type, "actor_id": self.actor_id,
            "description": self.description,
            "milestone_index": self.milestone_index,
            "details": self.details, "timestamp": self.timestamp,
        }


@dataclass
class TransactionOutcome:
    status: str = ""                  # settled | failed | cancelled
    value_realized: ConnectionValueVector = field(default_factory=ConnectionValueVector)
    relationship_growth: str = ""
    reputation_delta_a: float = 0.0
    reputation_delta_b: float = 0.0
    notes: str = ""
    recorded_at: str = ""

    def __post_init__(self):
        if not self.recorded_at: self.recorded_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "status": self.status,
            "value_realized": self.value_realized.to_dict(),
            "relationship_growth": self.relationship_growth,
            "reputation_delta_a": round(self.reputation_delta_a, 2),
            "reputation_delta_b": round(self.reputation_delta_b, 2),
            "notes": self.notes, "recorded_at": self.recorded_at,
        }


@dataclass
class UniverseTransaction:
    transaction_id: str = ""
    node_a_id: str = ""               # buyer / initiator
    node_b_id: str = ""               # provider / partner
    node_a_name: str = ""
    node_b_name: str = ""
    scope: TransactionScope = field(default_factory=TransactionScope)
    linked_opportunity_id: str = ""   # C5.3 RelationshipOpportunity
    relationship_id: str = ""         # C5.2 Relationship (if exists)
    stage: str = "PROPOSED"
    previous_stage: str = ""
    expected_value: ConnectionValueVector = field(default_factory=ConnectionValueVector)
    milestone_count: int = 0
    milestones_completed: int = 0
    created_at: str = ""
    updated_at: str = ""

    STAGES = [
        "PROPOSED", "AGREED", "IN_PROGRESS", "DELIVERED",
        "REVIEWED", "SETTLED", "FAILED", "CANCELLED",
    ]

    # Valid transitions: stage -> set of event_types that move forward
    TRANSITIONS = {
        "PROPOSED":   {"agreed": "AGREED", "cancelled": "CANCELLED"},
        "AGREED":     {"started": "IN_PROGRESS", "cancelled": "CANCELLED"},
        "IN_PROGRESS": {"milestone_completed": "IN_PROGRESS", "delivered": "DELIVERED", "failed": "FAILED"},
        "DELIVERED":  {"reviewed": "REVIEWED", "failed": "FAILED"},
        "REVIEWED":   {"settled": "SETTLED", "failed": "FAILED"},
        "SETTLED":    {},
        "FAILED":     {},
        "CANCELLED":  {},
    }

    def __post_init__(self):
        if not self.transaction_id: self.transaction_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at: self.created_at = now
        if not self.updated_at: self.updated_at = now

    def can_transition(self, event_type: str) -> bool:
        return event_type in self.TRANSITIONS.get(self.stage, {})

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "node_a_id": self.node_a_id, "node_b_id": self.node_b_id,
            "node_a_name": self.node_a_name, "node_b_name": self.node_b_name,
            "scope": self.scope.to_dict(),
            "linked_opportunity_id": self.linked_opportunity_id,
            "relationship_id": self.relationship_id,
            "stage": self.stage, "previous_stage": self.previous_stage,
            "expected_value": self.expected_value.to_dict(),
            "milestone_count": self.milestone_count,
            "milestones_completed": self.milestones_completed,
            "created_at": self.created_at, "updated_at": self.updated_at,
        }


# ========== Transaction Store ==========

class TransactionEventStore:
    _instance = None

    def __init__(self):
        self._events: Dict[str, List[TransactionEvent]] = {}
        self._by_node: Dict[str, List[str]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    def append(self, event: TransactionEvent):
        self._events.setdefault(event.transaction_id, []).append(event)
        for nid in (event.actor_id,):
            if nid:
                self._by_node.setdefault(nid, [])
                self._by_node[nid].append(event.event_id)
        return event

    def get_events(self, transaction_id: str) -> List[TransactionEvent]:
        return self._events.get(transaction_id, [])

    @classmethod
    def reset(cls):
        cls._instance = None


# ========== Transaction Engine ==========

class TransactionEngine:
    _instance = None

    def __init__(self):
        self._transactions: Dict[str, UniverseTransaction] = {}
        self._node_tx: Dict[str, List[str]] = {}
        self._store = TransactionEventStore.get_instance()
        self._locks: Dict[str, Any] = {}  # per-transaction threading locks (C6-T1 concurrency)

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    # ---- Core API ----

    def propose(self, node_a_id: str, node_b_id: str, scope: Dict,
                node_a_name: str = "", node_b_name: str = "",
                linked_opportunity_id: str = "") -> UniverseTransaction:
        tx = UniverseTransaction(
            node_a_id=node_a_id, node_b_id=node_b_id,
            node_a_name=node_a_name or node_a_id,
            node_b_name=node_b_name or node_b_id,
            scope=TransactionScope(**{k: v for k, v in scope.items() if k in TransactionScope.__dataclass_fields__}),
            linked_opportunity_id=linked_opportunity_id,
        )
        # Inherit expected value from the linked C5.3 opportunity when available
        if linked_opportunity_id:
            try:
                from app.universe.relationship_intelligence import get_relationship_intelligence_engine
                opp = get_relationship_intelligence_engine().get_opportunity(linked_opportunity_id)
                if opp:
                    cv = opp.get("connection_value") or opp.get("expected_value", {})
                    tx.expected_value = ConnectionValueVector(
                        revenue=cv.get("revenue", 0),
                        capability=cv.get("capability", 0),
                        reputation=cv.get("reputation", 0),
                        knowledge=cv.get("knowledge", 0),
                        network=cv.get("network", 0),
                    )
            except Exception:
                pass
        # Milestones: default to 1-3 based on scope
        tx.milestone_count = max(1, min(3, tx.scope.timeline_days // 30 + 1))
        self._transactions[tx.transaction_id] = tx
        for nid in (node_a_id, node_b_id):
            self._node_tx.setdefault(nid, [])
            self._node_tx[nid].append(tx.transaction_id)

        # Try to link an existing C5.2 relationship between the nodes
        try:
            from app.universe.relationship_engine import get_relationship_engine
            rel = get_relationship_engine().get_relationship(node_a_id, node_b_id)
            if rel:
                tx.relationship_id = rel.relationship_id
        except Exception:
            pass

        self._record_event(tx, "proposed", node_a_id,
                           f"Transaction proposed: {tx.scope.title or tx.scope.category}")
        return tx

    def transition(self, transaction_id: str, event_type: str,
                   actor_id: str = "", description: str = "",
                   milestone_index: int = -1, details: Dict = None) -> TransactionEvent:
        tx = self._transactions.get(transaction_id)
        if not tx:
            raise ValueError(f"Transaction not found: {transaction_id}")
        if not tx.can_transition(event_type):
            raise ValueError(f"Invalid transition '{event_type}' from stage {tx.stage}")

        next_stage = tx.TRANSITIONS[tx.stage][event_type]
        tx.previous_stage = tx.stage
        tx.stage = next_stage
        tx.updated_at = datetime.now(timezone.utc).isoformat()

        if event_type == "milestone_completed":
            tx.milestones_completed += 1
            if milestone_index >= 0:
                details = details or {}
                details["milestone_index"] = milestone_index

        return self._record_event(tx, event_type, actor_id, description, milestone_index, details)

    def complete(self, transaction_id: str, status: str = "settled",
                 value_realized: Dict = None, relationship_growth: str = "",
                 reputation_delta_a: float = 0.0, reputation_delta_b: float = 0.0,
                 notes: str = "", actor_id: str = "") -> TransactionOutcome:
        # C6-T1 security: reputation deltas are NEVER client-controlled.
        # The engine computes them from the outcome only. Client values are ignored.
        lock = self._locks.setdefault(transaction_id, __import__("threading").Lock())
        with lock:
            tx = self._transactions.get(transaction_id)
            if not tx:
                raise ValueError(f"Transaction not found: {transaction_id}")
            if tx.stage in ("SETTLED", "FAILED", "CANCELLED"):
                # Idempotent: terminal states never re-run feedback.
                outcome = self.get_outcome(transaction_id)
                if outcome:
                    return outcome
                raise ValueError(f"Transaction already terminal: {tx.stage}")

            if status == "settled":
                if tx.stage not in ("REVIEWED", "DELIVERED", "IN_PROGRESS"):
                    raise ValueError(f"Cannot settle transaction in stage {tx.stage}")
                if tx.stage == "IN_PROGRESS":
                    self.transition(transaction_id, "delivered", actor_id, "Delivered")
                    self.transition(transaction_id, "reviewed", actor_id, "Reviewed")
                elif tx.stage == "DELIVERED":
                    self.transition(transaction_id, "reviewed", actor_id, "Reviewed")
                self.transition(transaction_id, "settled", actor_id, "Settled")
            elif status == "failed":
                if tx.stage not in ("IN_PROGRESS", "DELIVERED", "REVIEWED"):
                    raise ValueError(f"Cannot fail transaction in stage {tx.stage}")
                self.transition(transaction_id, "failed", actor_id, notes or "Failed")
            elif status == "cancelled":
                if tx.stage not in ("PROPOSED", "AGREED"):
                    raise ValueError(f"Cannot cancel transaction in stage {tx.stage}")
                self.transition(transaction_id, "cancelled", actor_id, notes or "Cancelled")
            else:
                raise ValueError(f"Invalid completion status: {status}")

            # Clamp realized value to [0,1]; clients cannot inject negatives or >1.
            vv = value_realized or {}
            clamped = {k: max(0.0, min(1.0, float(vv.get(k, 0.0) or 0.0)))
                       for k in ("revenue", "capability", "reputation", "knowledge", "network")}
            outcome = TransactionOutcome(
                status=status,
                value_realized=ConnectionValueVector(**clamped),
                relationship_growth=relationship_growth,
                # Only settled transactions add reputation; failed/cancelled add 0.
                reputation_delta_a=5.0 if status == "settled" else 0.0,
                reputation_delta_b=5.0 if status == "settled" else 0.0,
                notes=notes,
            )
            self._feedback_to_universe(tx, outcome)
            return outcome

    # ---- Feedback Loop ----

    def _feedback_to_universe(self, tx: UniverseTransaction, outcome: TransactionOutcome):
        """After a transaction completes, feed results back into Universe.

        Reputation: settled -> positive events; failed -> negative events.
        Memory: record a fact about the transaction.
        Opportunity Memory: record the outcome on the linked opportunity.
        Relationship: record collaboration event (if relationship exists).
        """
        try:
            from app.universe.reputation_engine import get_reputation_engine
            re = get_reputation_engine()
            if outcome.status == "settled":
                # C6-T1 anti-abuse: the transaction was settled by the parties themselves,
                # so the reputation events are self-reported (low weight) until externally verified.
                re.record_event(tx.node_a_id, "company", "customer_success",
                                f"Transaction completed: {tx.scope.title or tx.scope.category}", "self_report")
                re.record_event(tx.node_b_id, "company", "partnership_completed",
                                f"Delivered: {tx.scope.title or tx.scope.category}", "self_report")
            # C6-T1: failed/cancelled NEVER auto-deduct either party's reputation.
            # Disputes require external verification before any negative event.
        except Exception:
            pass

        try:
            from app.universe.memory_engine import get_memory_engine
            mem = get_memory_engine()
            mem.record_fact(
                node_id=tx.node_a_id, node_type="company",
                statement=f"{tx.node_b_name}: {tx.scope.title or tx.scope.category} -> {outcome.status}",
                category="transaction", source="transaction_engine")
        except Exception:
            pass

        if tx.linked_opportunity_id:
            try:
                from app.universe.opportunity_memory import get_opportunity_memory_engine
                om = get_opportunity_memory_engine()
                om.record_outcome(
                    opportunity_id=tx.linked_opportunity_id,
                    status="successful" if outcome.status == "settled" else "failed",
                    value_realized=outcome.value_realized,
                    relationship_growth=outcome.relationship_growth,
                    reputation_change_a=outcome.reputation_delta_a,
                    reputation_change_b=outcome.reputation_delta_b,
                    notes=outcome.notes,
                )
            except Exception:
                pass

        if tx.relationship_id and outcome.status == "settled":
            try:
                from app.universe.relationship_engine import get_relationship_engine
                reng = get_relationship_engine()
                reng.record_event(tx.relationship_id, "collaboration_completed",
                                  description=f"Transaction delivered: {tx.scope.title or tx.scope.category}",
                                  outcome_score=1.0)
            except Exception:
                pass

    # ---- Queries ----

    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        tx = self._transactions.get(transaction_id)
        return tx.to_dict() if tx else None

    def get_node_transactions(self, node_id: str) -> List[Dict]:
        ids = self._node_tx.get(node_id, [])
        result = []
        for tid in ids:
            tx = self._transactions.get(tid)
            if tx:
                d = tx.to_dict()
                d["events"] = [e.to_dict() for e in self._store.get_events(tid)]
                result.append(d)
        result.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return result

    def get_transaction_with_history(self, transaction_id: str) -> Optional[Dict]:
        d = self.get_transaction(transaction_id)
        if d is None: return None
        d["events"] = [e.to_dict() for e in self._store.get_events(transaction_id)]
        return d

    def get_outcome(self, transaction_id: str) -> Optional[TransactionOutcome]:
        tx = self._transactions.get(transaction_id)
        if not tx: return None
        # Outcome is derived from final stage
        if tx.stage == "SETTLED":
            return TransactionOutcome(status="settled")
        if tx.stage == "FAILED":
            return TransactionOutcome(status="failed")
        if tx.stage == "CANCELLED":
            return TransactionOutcome(status="cancelled")
        return None

    # ---- Helpers ----

    def _record_event(self, tx: UniverseTransaction, event_type: str,
                      actor_id: str = "", description: str = "",
                      milestone_index: int = -1, details: Dict = None) -> TransactionEvent:
        event = TransactionEvent(
            transaction_id=tx.transaction_id, event_type=event_type,
            actor_id=actor_id, description=description,
            milestone_index=milestone_index, details=details or {},
        )
        self._store.append(event)
        tx.updated_at = datetime.now(timezone.utc).isoformat()
        return event

    def seed_sample_data(self):
        """Create a sample transaction from an opportunity and complete it."""
        # Ensure a C5.3 opportunity exists
        try:
            from app.universe.relationship_intelligence import get_relationship_intelligence_engine
            ri = get_relationship_intelligence_engine()
            opp = ri.evaluate_pair("tx-company-a", "tx-company-b",
                                   "Alpha Buyer", "Beta Provider")
            oid = opp.opportunity_id
        except Exception:
            oid = ""

        tx = self.propose(
            "tx-company-a", "tx-company-b",
            scope={
                "category": "service", "title": "GEO visibility upgrade",
                "description": "90-day GEO optimization service",
                "budget_min": 50000, "budget_max": 120000,
                "timeline_days": 90,
                "deliverables": ["GEO audit", "Content plan", "Implementation", "Report"],
            },
            node_a_name="Alpha Buyer", node_b_name="Beta Provider",
            linked_opportunity_id=oid,
        )
        self.transition(tx.transaction_id, "agreed", "tx-company-a", "Agreed")
        self.transition(tx.transaction_id, "started", "tx-company-b", "Started")
        self.transition(tx.transaction_id, "milestone_completed", "tx-company-b", "Milestone 1/3")
        self.transition(tx.transaction_id, "milestone_completed", "tx-company-b", "Milestone 2/3")
        outcome = self.complete(
            tx.transaction_id, "settled",
            value_realized={"revenue": 0.35, "capability": 0.8, "reputation": 0.3, "knowledge": 0.4, "network": 0.6},
            relationship_growth="DISCOVERED->COLLABORATING",
            reputation_delta_a=5.0, reputation_delta_b=4.0,
            notes="Delivered all milestones, client satisfied",
        )
        return {
            "transaction": self.get_transaction_with_history(tx.transaction_id),
            "outcome": outcome.to_dict(),
        }

    @classmethod
    def reset(cls):
        cls._instance = None
        TransactionEventStore.reset()
        try:
            get_transaction_engine.cache_clear()
        except Exception:
            pass


@lru_cache()
def get_transaction_engine():
    return TransactionEngine.get_instance()
