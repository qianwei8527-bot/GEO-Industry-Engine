"""Test C5.4 Opportunity Memory Engine - Universe Learning Loop."""
import sys
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

from app.universe.opportunity_memory import (
    ConnectionValueVector, RelationshipOpportunityEvent,
    OpportunityOutcome, OpportunityMemoryEngine,
    OpportunityMemoryStore, LearningAdjustment,
    get_opportunity_memory_engine,
)
from app.universe.relationship_intelligence import (
    RelationshipIntelligenceEngine, get_relationship_intelligence_engine,
)
from app.universe.reputation_engine import ReputationEngine


class TestConnectionValueVector:
    def test_create(self):
        v = ConnectionValueVector(revenue=0.5, capability=0.8, reputation=0.3, knowledge=0.4, network=0.6)
        assert v.overall == 0.52
        d = v.to_dict()
        assert d["revenue"] == 0.5
        assert "overall" in d

    def test_from_expected_value(self):
        ev = {"capability_gain": 0.8, "growth_acceleration": 0.5, "strategic_value": 0.6}
        v = ConnectionValueVector.from_expected_value(ev)
        assert v.capability == 0.8
        assert v.revenue > 0


class TestRelationshipOpportunityEvent:
    def test_create(self):
        e = RelationshipOpportunityEvent(
            opportunity_id="opp-1", node_a_id="a", node_b_id="b",
            event_type="opportunity_created", confidence_before=0.75
        )
        assert e.event_id
        d = e.to_dict()
        assert d["event_type"] == "opportunity_created"

    def test_invalid_type(self):
        try:
            RelationshipOpportunityEvent(
                opportunity_id="opp-1", node_a_id="a", node_b_id="b",
                event_type="invalid_type"
            )
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestOpportunityOutcome:
    def test_create(self):
        o = OpportunityOutcome(
            opportunity_id="opp-1", node_a_id="a", node_b_id="b",
            status="successful",
            value_realized=ConnectionValueVector(revenue=0.5, capability=0.8, reputation=0.3, knowledge=0.4, network=0.6)
        )
        assert o.outcome_id
        d = o.to_dict()
        assert d["status"] == "successful"


class TestOpportunityMemoryEngine:
    def setup_method(self):
        OpportunityMemoryEngine.reset()
        RelationshipIntelligenceEngine.reset()
        ReputationEngine.reset()

    def test_created_accepted_outcome_chain(self):
        mem = get_opportunity_memory_engine()
        mem.record_created("opp-1", "a", "b", 0.75, "test")
        mem.record_accepted("opp-1", "a", "accepted")
        mem.record_outcome("opp-1", "successful",
            ConnectionValueVector(revenue=0.5, capability=0.8, reputation=0.3, knowledge=0.4, network=0.6),
            notes="done")
        lc = mem.get_lifecycle("opp-1")
        assert len(lc) == 3
        assert lc[0]["event_type"] == "opportunity_created"
        assert lc[1]["event_type"] == "accepted"
        assert lc[2]["event_type"] == "successful"

    def test_adjusted_confidence_improves(self):
        mem = get_opportunity_memory_engine()
        mem.record_created("opp-1", "a", "b", 0.72, "test")
        mem.record_accepted("opp-1", "a", "accepted")
        mem.record_outcome("opp-1", "successful",
            ConnectionValueVector(revenue=0.5, capability=0.8, reputation=0.3, knowledge=0.4, network=0.6))
        adjusted = mem.get_adjusted_confidence("opp-1", 0.72)
        assert adjusted > 0.72

    def test_node_stats(self):
        mem = get_opportunity_memory_engine()
        mem.record_created("opp-1", "a", "b", 0.75, "test")
        mem.record_accepted("opp-1", "a", "accepted")
        mem.record_outcome("opp-1", "successful",
            ConnectionValueVector(revenue=0.5, capability=0.8, reputation=0.3, knowledge=0.4, network=0.6))
        mem.record_created("opp-2", "a", "c", 0.45, "test2")
        mem.record_rejected("opp-2", "a", "rejected")
        stats = mem.get_node_stats("a")
        assert stats["total_opportunities"] == 5
        assert stats["accepted"] == 1
        assert stats["rejected"] == 1

    def test_seed_data(self):
        mem = get_opportunity_memory_engine()
        result = mem.seed_sample_data()
        assert len(result["opportunities"]) == 2
        assert result["node_stats"]["accepted"] == 1
        assert result["node_stats"]["rejected"] == 1


class TestC54Integration:
    def setup_method(self):
        OpportunityMemoryEngine.reset()
        RelationshipIntelligenceEngine.reset()
        ReputationEngine.reset()

    def test_evaluate_records_opportunity(self):
        ri = get_relationship_intelligence_engine()
        mem = get_opportunity_memory_engine()
        opp = ri.evaluate_pair("a", "b", "Alpha", "Beta")
        assert opp.opportunity_event_id
        lc = mem.get_lifecycle(opp.opportunity_id)
        assert len(lc) >= 1
        assert lc[0]["event_type"] == "opportunity_created"

    def test_full_learning_loop(self):
        ri = get_relationship_intelligence_engine()
        mem = get_opportunity_memory_engine()
        opp = ri.evaluate_pair("a", "b", "Alpha", "Beta")
        c1 = opp.confidence
        mem.record_accepted(opp.opportunity_id, "a", "accepted")
        mem.record_outcome(opp.opportunity_id, "successful",
            ConnectionValueVector(revenue=0.5, capability=0.8, reputation=0.3, knowledge=0.4, network=0.6))
        adjusted = mem.get_adjusted_confidence(opp.opportunity_id, c1)
        assert adjusted > c1
        stats = mem.get_node_stats("a")
        assert stats["success_rate"] > 0

    def test_connection_value_in_opportunity(self):
        ri = get_relationship_intelligence_engine()
        opp = ri.evaluate_pair("a", "b", "Alpha", "Beta")
        cv = opp.connection_value
        assert isinstance(cv, dict)
        assert "overall" in cv
        assert "capability" in cv
