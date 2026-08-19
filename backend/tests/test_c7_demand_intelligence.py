"""C7 Demand Intelligence: DemandEvent model + gap analysis."""

import sys, uuid
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select

from app.database import _get_session_factory
from app.models.company import Company
from app.models.capability import Capability
from app.models.evidence import Evidence
from app.models.reputation import Reputation
from app.services.demand_intelligence import DemandIntelligenceService


class TestDemandIntelligence:
    async def _company(self, db):
        return (await db.execute(select(Company).limit(1))).scalars().first()

    async def test_create_real_event(self):
        factory = _get_session_factory()
        async with factory() as db:
            ev = await DemandIntelligenceService().create_event(db, {
                "actor_type": "parent",
                "scenario": "升学规划",
                "question_text": "科技特长生值得报吗",
                "missing_capability": "certify",
                "objective": "选择机构",
                "pain": "信息不透明",
            })
            assert ev["truth_status"] == "observed"
            assert ev["may_affect_real_metrics"] is True
            assert ev["event_id"]

    async def test_create_synthetic_is_isolated(self):
        factory = _get_session_factory()
        async with factory() as db:
            ev = await DemandIntelligenceService().create_event(db, {
                "actor_type": "parent",
                "scenario": "仿真",
                "question_text": "仿真需求",
                "missing_capability": "test",
                "is_synthetic": True,
            })
            assert ev["truth_status"] == "synthetic"
            assert ev["may_affect_real_metrics"] is False

    async def test_create_requires_fields(self):
        factory = _get_session_factory()
        async with factory() as db:
            with pytest.raises(ValueError):
                await DemandIntelligenceService().create_event(db, {"actor_type": "parent"})

    async def test_gap_analysis_matches_capability_node(self):
        factory = _get_session_factory()
        async with factory() as db:
            company = await self._company(db)
            if not company:
                return
            cap_name = f"demand-test-{uuid.uuid4().hex[:6]}"
            db.add(Capability(company_id=company.id, name=cap_name, level=1, category="test"))
            for i in range(5):
                db.add(Evidence(entity_id=company.id, entity_type="company",
                                 claim=f"gap clue {i}", source_url="https://universe.test/gap",
                                 source_type="other", truth_status="observed"))
            db.add(Reputation(node_id=company.id, node_type="company", total_score=60, reputation_level="B"))
            await db.commit()
            ev = await DemandIntelligenceService().create_event(db, {
                "actor_type": "enterprise",
                "scenario": "能力采购",
                "question_text": "需要该能力",
                "missing_capability": cap_name,
            })
            result = await DemandIntelligenceService().analyze(db, ev["id"])
            assert result["matched_count"] >= 1
            assert any(m["node_id"] == str(company.id) for m in result["matched_nodes"])
            assert result["gap_score"] < 1.0
            assert result["universe_rule"]

    async def test_list_events(self):
        factory = _get_session_factory()
        async with factory() as db:
            await DemandIntelligenceService().create_event(db, {
                "actor_type": "student",
                "scenario": "课程选择",
                "question_text": "选哪门课",
                "missing_capability": "research",
            })
            events = await DemandIntelligenceService().list_events(db, limit=5)
            assert len(events) >= 1
