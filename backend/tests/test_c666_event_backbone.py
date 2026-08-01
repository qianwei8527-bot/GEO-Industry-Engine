"""C6.6.6 Event Backbone validation: certification event penetrates Law -> Reputation -> Position -> Timeline."""
import sys
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select
from app.database import _get_session_factory
from app.universe.event_backbone import UniverseEvent, get_event_backbone
from app.universe.law_engine import UniverseLawEngine, get_law_engine
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine
from app.universe.memory_engine import MemoryEngine, get_memory_engine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine
from app.models.company import Company


class TestEventBackboneValidation:
    def setup_method(self):
        ReputationEngine.reset(); MemoryEngine.reset(); RelationshipIntelligenceEngine.reset()
        UniverseLawEngine.reset()

    async def test_certification_penetrates_universe(self):
        factory = _get_session_factory()
        async with factory() as db:
            c = (await db.execute(select(Company).limit(1))).scalars().first()
            if not c: pytest.skip("no company")
            nid = str(c.id)
            re = get_reputation_engine()
            before = re.get_profile(nid).overall_score if re.get_profile(nid) else 0
            engine = get_law_engine()
            event = UniverseEvent(node_id=nid, domain="certification", event_type="certification.approved",
                                 actor_id="system", source="demo", payload={"cert": "GEO-L3"})
            result = await engine.handle(event, context={"evidence_status": "verified"})
            assert result["matched"] is True
            assert "certification_trust_growth" in result["applied_laws"]
            # 1. Reputation changed by law (event recorded + recalculated)
            after = re.get_profile(nid).overall_score if re.get_profile(nid) else 0
            assert after >= before, f"reputation must not decrease: {before} -> {after}"
            law_events = [e for e in re.get_history(nid) if "Law certification_trust_growth" in e.get("description", "")]
            assert len(law_events) >= 1
            # 2. Position recompute executed
            pos_effects = [e for e in result["mutations"][0]["applied"] if e.get("engine") == "position"]
            assert pos_effects
            # 3. Memory story written
            facts = get_memory_engine().get_facts(nid, category="law")
            assert any("信任基础建立" in f.statement for f in facts)
            # 4. Backbone timeline has the event with correlation_id
            tl = get_event_backbone().timeline(nid)
            assert any(e["event_type"] == "certification.approved" and e["correlation_id"] == event.correlation_id for e in tl)

    async def test_unmatched_event_has_no_effect(self):
        factory = _get_session_factory()
        async with factory() as db:
            c = (await db.execute(select(Company).limit(1))).scalars().first()
            if not c: pytest.skip("no company")
            engine = get_law_engine()
            event = UniverseEvent(node_id=str(c.id), domain="observation", event_type="observation.new", source="demo")
            result = await engine.handle(event)
            assert result["matched"] is False
            assert result["mutations"] == []