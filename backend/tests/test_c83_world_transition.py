"""C8.3 World State Transition Engine tests."""

import sys, uuid
from contextlib import asynccontextmanager
from pathlib import Path as FsPath
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
import yaml
from sqlalchemy import select, delete

from app.database import _get_session_factory
from app.models.company import Company
from app.models.entity import Entity
from app.models.evidence import Evidence
from app.models.demand_event import DemandEvent
from app.models.connection_candidate import ConnectionCandidate
from app.models.world_model_contract import (
    VerticalWorld, VerticalWorldVersion, WorldBinding, WorldBindingEvidence,
)
from app.services.world_model_contract import WorldModelContractService
from app.services.evidence_claim import EvidenceClaimService
from app.services.trust_foundation import TrustFoundationService
from app.services.world_state import WorldStateService
from app.services.world_transition import WorldTransitionService

FIXTURE = FsPath(r"D:\GEO-Industry-Engine\config\universe\worlds\edu_tech_admission\1.0.0.yaml")


def _load_package():
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _code(prefix="c83"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestWorldTransition:
    @asynccontextmanager
    async def _company_scope(self, db):
        company = Company(
            geo_id=f"c83-{uuid.uuid4().hex}", entity_type="company",
            name=f"C83 {uuid.uuid4().hex[:6]}", region="test",
            industry_id=None, geo_score=0,
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
        cid = str(company.id)
        try:
            yield company
        finally:
            cuuid = company.id
            await db.execute(delete(ConnectionCandidate).where(ConnectionCandidate.target_node_id == cid))
            await db.execute(delete(WorldBindingEvidence).where(WorldBindingEvidence.binding_id.in_(
                select(WorldBinding.id).where(WorldBinding.entity_id == cid)
            )))
            await db.execute(delete(WorldBinding).where(WorldBinding.entity_id == cid))
            await db.execute(delete(Evidence).where(Evidence.entity_id == cuuid))
            await db.execute(delete(Company).where(Company.id == cuuid))
            await db.execute(delete(Entity).where(Entity.id == cuuid))
            await db.commit()

    async def _world(self, db):
        package = _load_package()
        code = _code()
        svc = WorldModelContractService()
        await svc.create_world(db, code, package["world"]["name"])
        await svc.create_draft(db, code, "1.0.0", package, source_file=str(FIXTURE))
        return code, svc

    async def _verified_claim(self, db, company, object_code="role_provider"):
        ev = Evidence(
            entity_id=company.id, entity_type="company", claim="GEO 案例",
            source_url="https://universe.test/verified", source_type="system_record",
            truth_status="observed", may_affect_real_metrics=True,
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        await TrustFoundationService().verify_evidence(
            db, str(ev.id), str(uuid.uuid4()), method="universe_record_crosscheck", result="approved"
        )
        claim = await EvidenceClaimService().create_claim(
            db, str(ev.id), "company", str(company.id), "provides_capability",
            "concept", object_code, claim_text="GEO 案例"
        )
        await EvidenceClaimService().verify_claim(db, claim["id"], str(uuid.uuid4()))
        return claim

    async def _bind(self, db, code, company, concept, claim_ids=None, truth="observed"):
        return await WorldModelContractService().create_binding(
            db, code, "1.0.0", "company", str(company.id), concept,
            truth_status=truth, evidence_claim_ids=claim_ids or [],
        )

    async def _demand(self, db, missing, truth="verified"):
        d = DemandEvent(
            event_id=str(uuid.uuid4()), actor_type="enterprise", scenario="test",
            question_text="q", missing_capability=missing,
            truth_status=truth, may_affect_real_metrics=(truth != "synthetic"),
            is_synthetic=(truth == "synthetic"), outcome="pending",
        )
        db.add(d)
        await db.commit()
        await db.refresh(d)
        return d

    async def _state(self, db, code, as_of):
        return await WorldStateService().generate(db, code, "1.0.0", "production", as_of)

    async def test_same_state_zero_changes(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, _ = await self._world(db)
            s1 = await self._state(db, code, "2026-01-01T00:00:00+00:00")
            s2 = await self._state(db, code, "2026-01-02T00:00:00+00:00")
            t = await WorldTransitionService().generate(db, s1["snapshot_id"], s2["snapshot_id"])
            assert t["compatibility_result"] == "comparable"
            assert t["change_manifest"] == []
            assert t["fully_auditable"] is True

    async def test_non_comparable_version_and_scope(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, svc = await self._world(db)
            s1 = await self._state(db, code, "2026-01-01T00:00:00+00:00")
            modified = _load_package()
            modified["world"]["name"] = "v2"
            await svc.create_draft(db, code, "2.0.0", modified)
            s2 = await WorldStateService().generate(db, code, "2.0.0", "production", "2026-01-02T00:00:00+00:00")
            t = await WorldTransitionService().generate(db, s1["snapshot_id"], s2["snapshot_id"])
            assert t["compatibility_result"] == "non_comparable"
            assert "world_version_mismatch_is_model_diff" in (t["non_comparable_reason"] or [])
            s3 = await WorldStateService().generate(db, code, "1.0.0", "observation", "2026-01-02T00:00:00+00:00")
            t2 = await WorldTransitionService().generate(db, s1["snapshot_id"], s3["snapshot_id"])
            assert t2["compatibility_result"] == "non_comparable"
            assert "state_scope_mismatch" in (t2["non_comparable_reason"] or [])

    async def test_gap_lifecycle(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                cap_code = f"cap_{uuid.uuid4().hex[:6]}"
                package = _load_package()
                package["concepts"].append({"code": cap_code, "type": "capability", "name": cap_code})
                package["relations"].append({"from": "evidence_cases", "to": cap_code, "type": "validates"})
                code = _code("gap")
                svc = WorldModelContractService()
                await svc.create_world(db, code, package["world"]["name"])
                await svc.create_draft(db, code, "1.0.0", package, source_file="custom")
                s1 = await self._state(db, code, "2026-01-01T00:00:00+00:00")
                await self._demand(db, cap_code, truth="verified")
                s2 = await self._state(db, code, "2026-01-02T00:00:00+00:00")
                s2b = await self._state(db, code, "2026-01-03T00:00:00+00:00")
                claim = await self._verified_claim(db, company, object_code=cap_code)
                await self._bind(db, code, company, cap_code, [claim["id"]], truth="verified")
                s3 = await self._state(db, code, "2026-01-04T00:00:00+00:00")

                opened = await WorldTransitionService().generate(db, s1["snapshot_id"], s2["snapshot_id"])
                persisted = await WorldTransitionService().generate(db, s2["snapshot_id"], s2b["snapshot_id"])
                resolved = await WorldTransitionService().generate(db, s2b["snapshot_id"], s3["snapshot_id"])
                assert any(g["status"] == "gap_opened" and g["gap_type"] == "capability_gap" for g in opened["gap_lifecycle"])
                assert any(g["status"] == "gap_persisted" for g in persisted["gap_lifecycle"])
                assert any(g["status"] == "gap_resolved" and g["gap_type"] == "capability_gap" for g in resolved["gap_lifecycle"])

    async def test_transition_hash_idempotent(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, _ = await self._world(db)
            s1 = await self._state(db, code, "2026-01-01T00:00:00+00:00")
            s2 = await self._state(db, code, "2026-01-02T00:00:00+00:00")
            a = await WorldTransitionService().generate(db, s1["snapshot_id"], s2["snapshot_id"])
            b = await WorldTransitionService().generate(db, s1["snapshot_id"], s2["snapshot_id"])
            assert a["transition_hash"] == b["transition_hash"]
            assert a["transition_id"] == b["transition_id"]

    async def test_source_drift_reported(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, _ = await self._world(db)
            s1 = await self._state(db, code, "2026-01-01T00:00:00+00:00")
            s2 = await self._state(db, code, "2026-01-02T00:00:00+00:00")
            from app.models.world_state_snapshot import WorldStateSnapshot
            row = (await db.execute(select(WorldStateSnapshot).where(WorldStateSnapshot.snapshot_id == s2["snapshot_id"]))).scalars().first()
            row.is_stale = True
            await db.commit()
            t = await WorldTransitionService().generate(db, s1["snapshot_id"], s2["snapshot_id"])
            assert t["historical_source_drift"] is True
            assert t["fully_auditable"] is False

    async def test_no_causal_or_trend_language(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, _ = await self._world(db)
            s1 = await self._state(db, code, "2026-01-01T00:00:00+00:00")
            s2 = await self._state(db, code, "2026-01-02T00:00:00+00:00")
            t = await WorldTransitionService().generate(db, s1["snapshot_id"], s2["snapshot_id"])
            text = yaml.safe_dump(t, allow_unicode=True)
            for forbidden in ("增长", "衰退", "趋势", "机会", "推荐", "cause", "trend"):
                assert forbidden not in text
