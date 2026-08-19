"""C7.4-R Demand Connection hardening tests."""

import sys, uuid
from contextlib import asynccontextmanager
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError

from app.database import _get_session_factory
from app.models.company import Company
from app.models.entity import Entity
from app.models.capability import Capability
from app.models.evidence import Evidence
from app.models.reputation import Reputation
from app.models.reputation_event_record import ReputationEventRecord
from app.models.demand_event import DemandEvent
from app.models.connection_candidate import ConnectionCandidate
from app.services.demand_intelligence import DemandIntelligenceService
from app.services.demand_connection import DemandConnectionService
from app.services.trust_foundation import TrustFoundationService


class TestDemandConnection:
    async def _create_company(self, db):
        company = Company(
            geo_id=f"c74-{uuid.uuid4().hex}",
            entity_type="company",
            name=f"C74 {uuid.uuid4().hex[:6]}",
            region="test",
            industry_id=None,
            geo_score=0,
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    async def _cleanup_company(self, db, company_id: str):
        cid_uuid = uuid.UUID(company_id)
        await db.execute(delete(ConnectionCandidate).where(ConnectionCandidate.target_node_id == company_id))
        await db.execute(delete(Evidence).where(Evidence.entity_id == cid_uuid))
        await db.execute(delete(Capability).where(Capability.company_id == cid_uuid))
        await db.execute(delete(Reputation).where(Reputation.node_id == cid_uuid))
        await db.execute(delete(Company).where(Company.id == cid_uuid))
        await db.execute(delete(Entity).where(Entity.id == cid_uuid))
        await db.commit()

    @asynccontextmanager
    async def _company_scope(self, db):
        company = await self._create_company(db)
        company_id = str(company.id)
        try:
            yield company
        finally:
            await self._cleanup_company(db, company_id)

    async def _cap(self, db, company, name):
        db.add(Capability(company_id=company.id, name=name, level=3, category="test"))
        await db.commit()

    async def _evidence(self, db, company, count, truth="observed", synthetic=False):
        rows = []
        for i in range(count):
            ev = Evidence(
                entity_id=company.id, entity_type="company",
                claim=f"c74 {truth} {uuid.uuid4().hex[:6]}",
                source_url=f"https://universe.test/{truth}/{i}",
                source_type="system_record", truth_status=truth,
                is_synthetic=synthetic,
                may_affect_real_metrics=(not synthetic),
            )
            db.add(ev)
            rows.append(ev)
        await db.commit()
        for ev in rows:
            await db.refresh(ev)
        if truth == "verified":
            for ev in rows:
                await TrustFoundationService().verify_evidence(
                    db, str(ev.id), str(uuid.uuid4()),
                    method="universe_record_crosscheck", result="approved"
                )
        return rows

    async def _verified_demand(self, db, cap_name):
        demand = await DemandIntelligenceService().create_event(db, {
            "actor_type": "enterprise", "scenario": "采购", "question_text": "需要能力",
            "missing_capability": cap_name,
        })
        row = await db.get(DemandEvent, uuid.UUID(demand["id"]))
        row.truth_status = "verified"
        row.may_affect_real_metrics = True
        await db.commit()
        return demand

    async def test_generate_idempotent_and_clamped(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                await self._evidence(db, company, 1, truth="verified")
                demand = await self._verified_demand(db, cap_name)
                svc = DemandConnectionService()
                first = await svc.generate(db, demand["id"])
                second = await svc.generate(db, demand["id"])
                assert first["generated"] >= 1
                assert second["generated"] == first["generated"]
                cand = first["candidates"][0]
                for key in ("capability_score", "evidence_score", "reputation_score", "trust_score", "connection_score"):
                    assert 0 <= cand[key] <= 1
                assert cand["truth_status"] == "verified"
                assert cand["may_affect_real_metrics"] is True
                assert cand["evidence_score"] == pytest.approx(round(1 / 3, 4))
                assert cand["config_version"] == "1.1.0"
                assert cand["config_hash"]

    async def test_only_verified_evidence_raises_score(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-only-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                await self._evidence(db, company, 5, truth="observed")
                await self._evidence(db, company, 2, truth="synthetic", synthetic=True)
                demand = await self._verified_demand(db, cap_name)
                result = await DemandConnectionService().generate(db, demand["id"])
                cand = result["candidates"][0]
                assert cand["evidence_score"] == 0.0
                assert cand["observed_evidence_count"] >= 5
                assert cand["synthetic_evidence_count"] >= 2
                assert cand["truth_status"] == "synthetic"
                assert cand["may_affect_real_metrics"] is False

    async def test_verified_threshold_and_clamp(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-thr-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                await self._evidence(db, company, 6, truth="verified")
                demand = await self._verified_demand(db, cap_name)
                result = await DemandConnectionService().generate(db, demand["id"])
                cand = result["candidates"][0]
                assert cand["evidence_score"] == 1.0
                assert cand["truth_status"] == "verified"
                assert cand["may_affect_real_metrics"] is True

    async def test_synthetic_demand_isolated(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-syn-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                demand = await DemandIntelligenceService().create_event(db, {
                    "actor_type": "test", "scenario": "仿真", "question_text": "仿真需求",
                    "missing_capability": cap_name, "is_synthetic": True,
                })
                result = await DemandConnectionService().generate(db, demand["id"])
                cand = result["candidates"][0]
                assert cand["truth_status"] == "synthetic"
                assert cand["may_affect_real_metrics"] is False
                svc = DemandConnectionService()
                with pytest.raises(ValueError):
                    await svc.decide(db, cand["id"], "qualified", scope="production")
                sim = await svc.decide(db, cand["id"], "qualified", scope="simulation", reason="test")
                assert sim["status"] == "qualified"
                assert sim["decision_scope"] == "simulation"

    async def test_observed_only_clue_internal_scope(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-obs-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                demand = await DemandIntelligenceService().create_event(db, {
                    "actor_type": "enterprise", "scenario": "采购", "question_text": "需要能力",
                    "missing_capability": cap_name,
                })
                result = await DemandConnectionService().generate(db, demand["id"])
                cand = result["candidates"][0]
                assert cand["truth_status"] == "observed"
                assert cand["may_affect_real_metrics"] is False
                svc = DemandConnectionService()
                with pytest.raises(ValueError):
                    await svc.decide(db, cand["id"], "qualified", scope="production")
                internal = await svc.decide(db, cand["id"], "qualified", scope="internal", reason="clue")
                assert internal["status"] == "qualified"

    async def test_verified_decision_does_not_change_reputation(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-ver-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                await self._evidence(db, company, 3, truth="verified")
                demand = await self._verified_demand(db, cap_name)
                rep_before = (await db.execute(
                    select(Reputation).where(Reputation.node_id == company.id, Reputation.node_type == "company")
                    .order_by(Reputation.created_at.desc()).limit(1)
                )).scalars().first()
                score_before = rep_before.total_score if rep_before else 0
                ev_before = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == company.id))).scalar() or 0
                rep_events_before = (await db.execute(select(func.count(ReputationEventRecord.event_id)).where(ReputationEventRecord.node_id == str(company.id)))).scalar() or 0

                svc = DemandConnectionService()
                result = await svc.generate(db, demand["id"])
                cand = result["candidates"][0]
                assert cand["truth_status"] == "verified"
                await svc.decide(db, cand["id"], "qualified", scope="production", actor="reviewer-1")
                await svc.decide(db, cand["id"], "accepted", scope="production", actor="reviewer-1")
                await svc.decide(db, cand["id"], "completed", scope="production", actor="reviewer-1")

                rep_after = (await db.execute(
                    select(Reputation).where(Reputation.node_id == company.id, Reputation.node_type == "company")
                    .order_by(Reputation.created_at.desc()).limit(1)
                )).scalars().first()
                ev_after = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == company.id))).scalar() or 0
                rep_events_after = (await db.execute(select(func.count(ReputationEventRecord.event_id)).where(ReputationEventRecord.node_id == str(company.id)))).scalar() or 0
                assert (rep_after.total_score if rep_after else 0) == score_before
                assert ev_after == ev_before
                assert rep_events_after == rep_events_before

    async def test_database_unique_constraint(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-unq-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                demand = await DemandIntelligenceService().create_event(db, {
                    "actor_type": "enterprise", "scenario": "采购", "question_text": "需要能力",
                    "missing_capability": cap_name,
                })
                result = await DemandConnectionService().generate(db, demand["id"])
                cand = result["candidates"][0]
                count = (await db.execute(select(func.count(ConnectionCandidate.id)).where(
                    ConnectionCandidate.demand_event_id == uuid.UUID(demand["id"]),
                    ConnectionCandidate.target_node_id == cand["target_node_id"],
                ))).scalar()
                assert count == 1
                duplicate = ConnectionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    demand_event_id=uuid.UUID(demand["id"]),
                    target_node_id=cand["target_node_id"],
                    connection_type=cand["connection_type"],
                    deduplication_hash="other-hash",
                    truth_status="observed",
                )
                db.add(duplicate)
                with pytest.raises(IntegrityError):
                    await db.commit()
                await db.rollback()

    async def test_outcome_writeback_no_auto_evidence(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_name = f"c74-out-{uuid.uuid4().hex[:6]}"
                await self._cap(db, company, cap_name)
                demand = await DemandIntelligenceService().create_event(db, {
                    "actor_type": "enterprise", "scenario": "采购", "question_text": "需要能力",
                    "missing_capability": cap_name,
                })
                result = await DemandConnectionService().generate(db, demand["id"])
                cand = result["candidates"][0]
                ev_before = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == company.id))).scalar() or 0
                updated = await DemandConnectionService().record_outcome(db, cand["id"], "won", actor="reviewer-1")
                assert updated["outcome"] == "won"
                demand_row = await db.get(DemandEvent, uuid.UUID(demand["id"]))
                assert demand_row.outcome == "won"
                ev_after = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == company.id))).scalar() or 0
                assert ev_after == ev_before
