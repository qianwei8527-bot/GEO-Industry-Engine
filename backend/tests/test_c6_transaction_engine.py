"""Test C6 Transaction Engine - opportunity to delivered outcome loop."""
import sys
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

from app.universe.transaction_engine import (
    TransactionScope, TransactionEvent, TransactionOutcome,
    UniverseTransaction, TransactionEngine, TransactionEventStore,
    get_transaction_engine,
)
from app.universe.opportunity_memory import (
    OpportunityMemoryEngine, get_opportunity_memory_engine, ConnectionValueVector,
)
from app.universe.relationship_intelligence import (
    RelationshipIntelligenceEngine, get_relationship_intelligence_engine,
)
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine
from app.universe.memory_engine import MemoryEngine, get_memory_engine


class TestTransactionScope:
    def test_create(self):
        s = TransactionScope(category="service", title="GEO audit", budget_min=100, budget_max=500)
        d = s.to_dict()
        assert d["category"] == "service"
        assert d["budget_max"] == 500


class TestTransactionEvent:
    def test_create(self):
        e = TransactionEvent(transaction_id="tx-1", event_type="proposed")
        assert e.event_id
        assert e.to_dict()["event_type"] == "proposed"

    def test_invalid_type(self):
        try:
            TransactionEvent(transaction_id="tx-1", event_type="nope")
            assert False, "should raise"
        except ValueError:
            pass


class TestUniverseTransaction:
    def test_stages(self):
        tx = UniverseTransaction(node_a_id="a", node_b_id="b")
        assert tx.stage == "PROPOSED"
        assert tx.can_transition("agreed")
        assert not tx.can_transition("settled")


class TestTransactionEngine:
    def setup_method(self):
        TransactionEngine.reset()
        OpportunityMemoryEngine.reset()
        RelationshipIntelligenceEngine.reset()
        ReputationEngine.reset()
        MemoryEngine.reset()

    def test_propose(self):
        eng = get_transaction_engine()
        tx = eng.propose("a", "b", {"category": "service", "title": "X", "timeline_days": 60})
        assert tx.stage == "PROPOSED"
        assert tx.milestone_count >= 1
        assert tx.created_at

    def test_full_lifecycle(self):
        eng = get_transaction_engine()
        tx = eng.propose("a", "b", {"category": "service", "title": "GEO", "timeline_days": 30})
        eng.transition(tx.transaction_id, "agreed", "a")
        eng.transition(tx.transaction_id, "started", "b")
        eng.transition(tx.transaction_id, "milestone_completed", "b")
        eng.transition(tx.transaction_id, "delivered", "b")
        eng.transition(tx.transaction_id, "reviewed", "a")
        eng.transition(tx.transaction_id, "settled", "a")
        d = eng.get_transaction(tx.transaction_id)
        assert d["stage"] == "SETTLED"
        assert d["milestones_completed"] == 1

    def test_complete_settled(self):
        eng = get_transaction_engine()
        tx = eng.propose("a", "b", {"category": "service", "title": "GEO"})
        eng.transition(tx.transaction_id, "agreed", "a")
        eng.transition(tx.transaction_id, "started", "b")
        eng.transition(tx.transaction_id, "milestone_completed", "b")
        outcome = eng.complete(tx.transaction_id, "settled",
            value_realized={"revenue": 0.4, "capability": 0.8, "reputation": 0.3, "knowledge": 0.4, "network": 0.6})
        assert outcome.status == "settled"
        d = eng.get_transaction(tx.transaction_id)
        assert d["stage"] == "SETTLED"

    def test_feedback_to_reputation(self):
        eng = get_transaction_engine()
        tx = eng.propose("a", "b", {"category": "service", "title": "GEO"})
        eng.transition(tx.transaction_id, "agreed", "a")
        eng.transition(tx.transaction_id, "started", "b")
        eng.complete(tx.transaction_id, "settled")
        re = get_reputation_engine()
        events_a = [e for e in re.get_history("a") if "Transaction completed" in e.get("description", "")]
        assert len(events_a) >= 1
        mem = get_memory_engine()
        facts = mem.get_facts("a", category="transaction")
        assert len(facts) >= 1

    def test_feedback_to_opportunity_memory(self):
        eng = get_transaction_engine()
        ri = get_relationship_intelligence_engine()
        opp = ri.evaluate_pair("a", "b", "Alpha", "Beta")
        tx = eng.propose("a", "b", {"category": "service", "title": "GEO"}, linked_opportunity_id=opp.opportunity_id)
        eng.transition(tx.transaction_id, "agreed", "a")
        eng.transition(tx.transaction_id, "started", "b")
        eng.complete(tx.transaction_id, "settled")
        om = get_opportunity_memory_engine()
        outcome = om.get_outcome(opp.opportunity_id)
        assert outcome is not None
        assert outcome["status"] == "successful"

    def test_failed_transaction(self):
        # C6-T1: failed marks the transaction FAILED and records memory,
        # but NEVER auto-deducts either party's reputation.
        eng = get_transaction_engine()
        tx = eng.propose("a", "b", {"category": "service", "title": "GEO"})
        eng.transition(tx.transaction_id, "agreed", "a")
        eng.transition(tx.transaction_id, "started", "b")
        outcome = eng.complete(tx.transaction_id, "failed")
        assert outcome.status == "failed"
        assert outcome.reputation_delta_a == 0.0
        assert outcome.reputation_delta_b == 0.0
        d = eng.get_transaction(tx.transaction_id)
        assert d["stage"] == "FAILED"
        re = get_reputation_engine()
        negative_a = [e for e in re.get_history("a") if e.get("event_type") in ("customer_failure", "partnership_terminated")]
        negative_b = [e for e in re.get_history("b") if e.get("event_type") in ("customer_failure", "partnership_terminated")]
        assert len(negative_a) == 0
        assert len(negative_b) == 0
        mem = get_memory_engine()
        facts = mem.get_facts("a", category="transaction")
        assert len(facts) >= 1

    def test_node_transactions(self):
        eng = get_transaction_engine()
        eng.propose("a", "b", {"category": "service", "title": "T1"})
        eng.propose("a", "c", {"category": "data", "title": "T2"})
        txs = eng.get_node_transactions("a")
        assert len(txs) == 2

    def test_seed_data(self):
        eng = get_transaction_engine()
        result = eng.seed_sample_data()
        assert result["transaction"]["stage"] == "SETTLED"
        assert result["outcome"]["status"] == "settled"


class TestC6T1Security:
    def setup_method(self):
        TransactionEngine.reset()
        OpportunityMemoryEngine.reset()
        RelationshipIntelligenceEngine.reset()
        ReputationEngine.reset()
        MemoryEngine.reset()

    def _propose_and_start(self, eng, a="sec-a", b="sec-b"):
        tx = eng.propose(a, b, {"category": "service", "title": "GEO"})
        eng.transition(tx.transaction_id, "agreed", a)
        eng.transition(tx.transaction_id, "started", b)
        return tx

    def test_client_reputation_delta_ignored(self):
        """C6-T1 anti-abuse: client cannot inject reputation deltas."""
        eng = get_transaction_engine()
        tx = self._propose_and_start(eng)
        outcome = eng.complete(tx.transaction_id, "settled",
                               reputation_delta_a=100.0, reputation_delta_b=99.0)
        # Server-computed: +5 for settled, never 100/99
        assert outcome.reputation_delta_a == 5.0
        assert outcome.reputation_delta_b == 5.0

    def test_value_realized_clamped(self):
        """C6-T1: value vectors are clamped to [0,1]."""
        eng = get_transaction_engine()
        tx = self._propose_and_start(eng)
        outcome = eng.complete(tx.transaction_id, "settled",
                               value_realized={"revenue": 99, "capability": -5, "reputation": 0.5})
        assert outcome.value_realized.revenue == 1.0
        assert outcome.value_realized.capability == 0.0
        assert outcome.value_realized.reputation == 0.5

    def test_failed_does_not_deduct_reputation(self):
        """C6-T1: failed must not auto-deduct either party reputation."""
        eng = get_transaction_engine()
        tx = self._propose_and_start(eng)
        outcome = eng.complete(tx.transaction_id, "failed")
        assert outcome.status == "failed"
        assert outcome.reputation_delta_a == 0.0
        assert outcome.reputation_delta_b == 0.0
        re = get_reputation_engine()
        events_a = re.get_history("sec-a")
        events_b = re.get_history("sec-b")
        assert all("customer_failure" not in e.get("event_type", "") for e in events_a)
        assert all("partnership_terminated" not in e.get("event_type", "") for e in events_b)

    def test_settled_reputation_is_self_reported(self):
        """C6-T1 anti-abuse: settled reputation events are self_report (low weight)."""
        eng = get_transaction_engine()
        tx = self._propose_and_start(eng)
        eng.complete(tx.transaction_id, "settled")
        re = get_reputation_engine()
        ev_a = [e for e in re.get_history("sec-a") if e.get("event_type") == "customer_success"]
        assert len(ev_a) >= 1
        assert all(e.get("source_type") == "self_report" for e in ev_a)

    def test_complete_idempotent(self):
        """C6-T1: second complete on terminal transaction returns without re-feedback."""
        eng = get_transaction_engine()
        tx = self._propose_and_start(eng)
        eng.complete(tx.transaction_id, "settled")
        re = get_reputation_engine()
        before = len(re.get_history("sec-a"))
        # Second complete must not add another reputation event
        try:
            eng.complete(tx.transaction_id, "settled")
        except ValueError:
            pass
        after = len(re.get_history("sec-a"))
        assert after == before


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))