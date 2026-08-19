"""C8.2 World State Engine tests."""

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

FIXTURE = FsPath(r"D:\GEO-Industry-Engine\config\universe\worlds\edu_tech_admission\1.0.0.yaml")


def _load_package():
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _code(prefix="c82"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestWorldState:
    @asynccontextmanager
    async def _company_scope(self, db):
        company = Company(
            geo_id=f"c82-{uuid.uuid4().hex}", entity_type="company",
            name=f"C82 {uuid.uuid4().hex[:6]}", region="test",
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

    async def _verified_claim(self, db, company, object_code="role_provider",
                              predicate="provides_capability"):
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
            db, str(ev.id), "company", str(company.id), predicate, "concept",
            object_code, claim_text="GEO 案例"
        )
        await EvidenceClaimService().verify_claim(db, claim["id"], str(uuid.uuid4()))
        return claim

    async def _bind(self, db, code, company, concept, claim_ids=None, truth="observed"):
        svc = WorldModelContractService()
        return await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                        concept, truth_status=truth,
                                        evidence_claim_ids=claim_ids or [])

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

    async def _connection(self, db, demand, target_id, status="completed", truth="verified"):
        c = ConnectionCandidate(
            candidate_id=str(uuid.uuid4()), demand_event_id=demand.id,
            target_node_id=str(target_id), connection_type="role_provider",
            truth_status=truth, status=status, decision_scope="production",
            may_affect_real_metrics=True, deduplication_hash=str(uuid.uuid4()),
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        return c

    async def test_multiple_claims_no_supply_inflation(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, _ = await self._world(db)
                c1 = await self._verified_claim(db, company, object_code="capability_guidance")
                c2 = await self._verified_claim(db, company, object_code="capability_guidance")
                await self._bind(db, code, company, "capability_guidance", [c1["id"], c2["id"]], truth="verified")
                state = await WorldStateService().generate(db, code, "1.0.0", "production")
                dims = state["dimensions"]
                assert dims["capability_supply"]["unique_pairs"] == 1
                assert dims["nodes"]["unique_count"] == 1

    async def test_same_node_two_roles_unique_nodes(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, _ = await self._world(db)
                r1 = await self._verified_claim(db, company, object_code="role_provider")
                r2 = await self._verified_claim(db, company, object_code="capability_guidance")
                await self._bind(db, code, company, "role_provider", [r1["id"]], truth="verified")
                await self._bind(db, code, company, "capability_guidance", [r2["id"]], truth="verified")
                state = await WorldStateService().generate(db, code, "1.0.0", "production")
                dims = state["dimensions"]
                assert dims["nodes"]["unique_count"] == 1
                assert dims["nodes"]["role_distribution"]["role_provider"] == 1
                assert dims["nodes"]["role_distribution"]["capability_guidance"] == 1

    async def test_capability_gap_and_observed_supply(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, _ = await self._world(db)
                await self._demand(db, "capability_guidance", truth="verified")
                await self._bind(db, code, company, "capability_guidance", truth="observed")
                state = await WorldStateService().generate(db, code, "1.0.0", "production")
                gap_types = [g["gap_type"] for g in state["gaps"]]
                assert "capability_gap" in gap_types
                assert "trust_gap" in gap_types

    async def test_connection_and_outcome_gap(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, _ = await self._world(db)
                demand = await self._demand(db, "role_provider", truth="verified")
                claim = await self._verified_claim(db, company, object_code="role_provider")
                await self._bind(db, code, company, "role_provider", [claim["id"]], truth="verified")
                state1 = await WorldStateService().generate(db, code, "1.0.0", "production")
                assert "connection_gap" in [g["gap_type"] for g in state1["gaps"]]
                await self._connection(db, demand, company.id, status="completed")
                state2 = await WorldStateService().generate(db, code, "1.0.0", "production")
                gap_types = [g["gap_type"] for g in state2["gaps"]]
                assert "connection_gap" not in gap_types
                assert "outcome_gap" in gap_types

    async def test_simulation_scope_isolated(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, _ = await self._world(db)
                await self._demand(db, "role_provider", truth="synthetic")
                production = await WorldStateService().generate(db, code, "1.0.0", "production")
                simulation = await WorldStateService().generate(db, code, "1.0.0", "simulation")
                assert "synthetic" not in production["truth_distribution"]
                assert "synthetic" in simulation["truth_distribution"]

    async def test_denominator_zero_not_applicable(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, _ = await self._world(db)
            state = await WorldStateService().generate(db, code, "1.0.0", "production")
            assert state["dimensions"]["evidence_claim"]["binding_coverage"] is None

    async def test_snapshot_hash_idempotent(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, _ = await self._world(db)
            a = await WorldStateService().generate(db, code, "1.0.0", "production", "2026-01-01T00:00:00+00:00")
            b = await WorldStateService().generate(db, code, "1.0.0", "production", "2026-01-01T00:00:00+00:00")
            assert a["snapshot_hash"] == b["snapshot_hash"]
            assert a["snapshot_id"] == b["snapshot_id"]

    async def test_fact_change_marks_stale(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, _ = await self._world(db)
                claim = await self._verified_claim(db, company, object_code="role_provider")
                await self._bind(db, code, company, "role_provider", [claim["id"]], truth="verified")
                snap = await WorldStateService().generate(db, code, "1.0.0", "production")
                ev = await db.get(Evidence, uuid.UUID(claim["evidence_id"]))
                ev.claim = ev.claim + " changed"
                await db.commit()
                integrity = await WorldStateService().check_integrity(db, snap["snapshot_id"])
                assert integrity["stale"] is True

    async def test_new_version_does_not_change_old_snapshot(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, svc = await self._world(db)
            snap = await WorldStateService().generate(db, code, "1.0.0", "production", "2026-01-01T00:00:00+00:00")
            modified = _load_package()
            modified["world"]["name"] = "v2"
            await svc.create_draft(db, code, "2.0.0", modified)
            again = await WorldStateService().generate(db, code, "1.0.0", "production", "2026-01-01T00:00:00+00:00")
            assert again["snapshot_hash"] == snap["snapshot_hash"]
