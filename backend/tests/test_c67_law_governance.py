"""C6.7 Law Governance: registry schema, conditions, conflict override, explanation."""
import sys
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select
from app.database import _get_session_factory
from app.universe.event_backbone import UniverseEvent
from app.universe.law_engine import UniverseLawEngine, get_law_engine
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine
from app.universe.memory_engine import MemoryEngine, get_memory_engine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine
from app.models.company import Company


class TestLawGovernance:
    def setup_method(self):
        ReputationEngine.reset(); MemoryEngine.reset(); RelationshipIntelligenceEngine.reset()
        UniverseLawEngine.reset()

    async def real_node(self):
        factory = _get_session_factory()
        async with factory() as db:
            c = (await db.execute(select(Company).limit(1))).scalars().first()
            return str(c.id) if c else None

    async def test_registry_full_schema(self):
        engine = get_law_engine()
        law = engine.registry.get("certification_trust_growth")
        assert law
        for field in ("law_id", "version", "status", "owner", "description", "priority",
                      "trigger", "conditions", "effects", "constraints", "audit"):
            assert field in law, "missing " + field
        assert len(engine.registry.laws) == 4

    async def test_verified_condition_raises_reputation(self):
        nid = await self.real_node()
        if not nid: pytest.skip("no node")
        engine = get_law_engine()
        event = UniverseEvent(node_id=nid, domain="certification", event_type="certification.approved",
                              actor_id="system", source="demo")
        result = await engine.handle(event, context={"evidence_status": "verified"})
        assert "certification_trust_growth" in result["applied_laws"]
        re = get_reputation_engine()
        law_events = [e for e in re.get_history(nid) if "Law certification_trust_growth" in e.get("description", "")]
        assert len(law_events) >= 1

    async def test_observed_condition_memory_only(self):
        nid = await self.real_node()
        if not nid: pytest.skip("no node")
        engine = get_law_engine()
        event = UniverseEvent(node_id=nid, domain="certification", event_type="certification.approved",
                              actor_id="system", source="demo")
        re = get_reputation_engine()
        before = len(re.get_history(nid))
        result = await engine.handle(event, context={"evidence_status": "observed"})
        assert "certification_memory_only" in result["applied_laws"]
        assert len(re.get_history(nid)) == before
        mem = get_memory_engine().get_facts(nid, category="law")
        assert any("未核验" in f.statement for f in mem)

    async def test_risk_applies_and_lowers_reputation(self):
        nid = await self.real_node()
        if not nid: pytest.skip("no node")
        engine = get_law_engine()
        ev_risk = UniverseEvent(node_id=nid, domain="complaint", event_type="complaint.verified", actor_id="system")
        r_risk = await engine.handle(ev_risk, context={"evidence_status": "verified"})
        assert "complaint_risk_override" in r_risk["applied_laws"]
        re = get_reputation_engine()
        neg = [e for e in re.get_history(nid) if e.get("event_type") == "negative_feedback"]
        assert len(neg) >= 1

    async def test_conflict_resolver_risk_wins(self):
        engine = get_law_engine()
        candidates = [{"law_id": "certification_trust_growth", "priority": 50},
                      {"law_id": "complaint_risk_override", "priority": 100}]
        resolution = engine.conflicts.resolve(candidates)
        applied = [l["law_id"] for l in resolution["applied"]]
        suppressed = [s["law_id"] for s in resolution["suppressed"]]
        assert "complaint_risk_override" in applied
        assert "certification_trust_growth" in suppressed
        assert any(s["reason"] == "risk_law_override" for s in resolution["suppressed"])

    async def test_explanation_chain(self):
        nid = await self.real_node()
        if not nid: pytest.skip("no node")
        engine = get_law_engine()
        event = UniverseEvent(node_id=nid, domain="certification", event_type="certification.approved", actor_id="system")
        result = await engine.handle(event, context={"evidence_status": "verified"})
        assert result["explanation"]
        exp = result["explanation"][0]
        assert exp["law"]["law_id"] == "certification_trust_growth"
        assert "event" in exp and "impacts" in exp and "confidence" in exp
