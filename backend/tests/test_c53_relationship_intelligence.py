"""
Test C5.3 Relationship Intelligence Engine

Covers:
  - RelationshipOpportunity data model
  - OpportunityEvaluator (pair evaluation)
  - RelationshipIntelligenceEngine (bulk + caching)
  - C5.1 Reputation integration
  - C5.2 Relationship integration
  - Risk detection rules
  - Confidence scoring
"""

import sys
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

from app.universe.relationship_intelligence import (
    RelationshipOpportunity,
    RiskSignal,
    NextStep,
    OpportunityEvaluator,
    RelationshipIntelligenceEngine,
    get_relationship_intelligence_engine,
)
from app.universe.reputation_engine import get_reputation_engine, ReputationEngine
from app.universe.relationship_engine import get_relationship_engine, RelationshipEngine


class TestRelationshipOpportunity:
    def test_create(self):
        opp = RelationshipOpportunity(
            node_a_id="a1", node_b_id="b1",
            node_a_name="Alpha", node_b_name="Beta",
        )
        assert opp.opportunity_id
        assert opp.confidence == 0.0
        assert opp.reasons == {}
        assert opp.risks == []
        assert opp.next_steps == []

    def test_to_dict(self):
        opp = RelationshipOpportunity(
            node_a_id="a1", node_b_id="b1",
            node_a_name="Alpha", node_b_name="Beta",
        )
        opp.risks.append(RiskSignal(category="test", severity="high", description="test risk"))
        opp.next_steps.append(NextStep(action="test action", rationale="test", timeframe="immediate"))
        d = opp.to_dict()
        assert d["node_a_name"] == "Alpha"
        assert d["node_b_name"] == "Beta"
        assert len(d["risks"]) == 1
        assert len(d["next_steps"]) == 1
        assert "confidence" in d
        assert "reasons" in d
        assert "existing_relationship" in d
        assert "expected_value" in d


class TestRiskSignal:
    def test_defaults(self):
        r = RiskSignal()
        assert r.severity == "low"
        assert r.category == ""

    def test_to_dict(self):
        r = RiskSignal(category="reputation", severity="high", description="test", mitigation="mit")
        d = r.to_dict()
        assert d["category"] == "reputation"
        assert d["severity"] == "high"


class TestNextStep:
    def test_to_dict(self):
        n = NextStep(action="do X", rationale="because Y", timeframe="short_term", expected_outcome="Z")
        d = n.to_dict()
        assert d["action"] == "do X"


class TestOpportunityEvaluator:
    def setup_method(self):
        RelationshipIntelligenceEngine.reset()
        ReputationEngine.reset()
        RelationshipEngine.reset()
        self.evaluator = OpportunityEvaluator()

    def test_evaluate_basic(self):
        opp = self.evaluator.evaluate("node-a", "node-b", "Alpha", "Beta")
        assert isinstance(opp, RelationshipOpportunity)
        assert opp.node_a_id == "node-a"
        assert opp.node_b_id == "node-b"
        assert 0 <= opp.confidence <= 1.0
        assert len(opp.recommended_action) > 0

    def test_evaluate_with_reputation(self):
        re = get_reputation_engine()
        re.record_event("node-a", "company", "certification_passed", "GEO certified", "government")
        re.record_event("node-a", "company", "customer_success", "Project done", "enterprise_customer")
        re.record_event("node-a", "company", "peer_endorsement", "Recommended", "partner")
        re.recalculate("node-a", "company")
        opp = self.evaluator.evaluate("node-a", "node-b", "Alpha", "Beta")
        assert opp.reasons.get("reputation_match", 0) >= 0

    def test_unknown_reputation_detected(self):
        opp = self.evaluator.evaluate("node-a", "unknown-node", "Alpha", "Unknown")
        risk_descriptions = [r.description for r in opp.risks]
        assert any("insufficient_reputation_data" in desc for desc in risk_descriptions)


class TestRelationshipIntelligenceEngine:
    def setup_method(self):
        RelationshipIntelligenceEngine.reset()
        ReputationEngine.reset()
        RelationshipEngine.reset()

    def test_singleton(self):
        e1 = get_relationship_intelligence_engine()
        e2 = get_relationship_intelligence_engine()
        assert e1 is e2

    def test_evaluate_pair(self):
        engine = get_relationship_intelligence_engine()
        opp = engine.evaluate_pair("a", "b", "Alpha", "Beta")
        assert opp.confidence >= 0

    def test_evaluate_candidates(self):
        engine = get_relationship_intelligence_engine()
        opps = engine.evaluate_candidates("a", ["b", "c", "d"], "Alpha")
        assert len(opps) == 3
        assert opps[0].confidence >= opps[1].confidence

    def test_get_opportunities(self):
        engine = get_relationship_intelligence_engine()
        engine.evaluate_pair("a", "b", "Alpha", "Beta")
        engine.evaluate_pair("a", "c", "Alpha", "Gamma")
        opps = engine.get_opportunities("a")
        assert len(opps) == 2

    def test_get_opportunity_by_id(self):
        engine = get_relationship_intelligence_engine()
        opp = engine.evaluate_pair("a", "b", "Alpha", "Beta")
        result = engine.get_opportunity(opp.opportunity_id)
        assert result is not None
        assert result["confidence"] == opp.confidence

    def test_seed_data(self):
        engine = get_relationship_intelligence_engine()
        result = engine.seed_sample_data()
        assert "opportunities" in result
        assert "summary" in result
        assert len(result["opportunities"]) == 2
        opp0 = result["opportunities"][0]
        assert "reasons" in opp0
        assert "risks" in opp0
        assert "next_steps" in opp0
        assert "recommended_action" in opp0


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))