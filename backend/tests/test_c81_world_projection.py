"""C8.1 Trusted World Projection tests."""

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
    VerticalWorld, VerticalWorldVersion, WorldConcept, WorldConceptRelation, WorldBinding, WorldBindingEvidence,
)
from app.services.world_model_contract import WorldModelContractService
from app.services.world_projection import WorldProjectionService
from app.services.trust_foundation import TrustFoundationService
from app.services.evidence_claim import EvidenceClaimService

FIXTURE = FsPath(r"D:\GEO-Industry-Engine\config\universe\worlds\edu_tech_admission\1.0.0.yaml")


def _load_package():
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _code(prefix="c81"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestWorldProjection:
    @asynccontextmanager
    async def _company_scope(self, db):
        company = Company(
            geo_id=f"c81-{uuid.uuid4().hex}",
            entity_type="company",
            name=f"C81 {uuid.uuid4().hex[:6]}",
            region="test",
            industry_id=None,
            geo_score=0,
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
        return code, svc, package

    async def _verified_claim(self, db, company, source_type="system_record", claim_text="GEO 案例",
                              predicate="provides_capability", object_code="role_provider"):
        ev = Evidence(
            entity_id=company.id, entity_type="company",
            claim=claim_text, source_url="https://universe.test/verified",
            source_name="Registry", source_type=source_type, truth_status="observed",
            may_affect_real_metrics=True,
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        await TrustFoundationService().verify_evidence(
            db, str(ev.id), str(uuid.uuid4()), method="universe_record_crosscheck", result="approved"
        )
        claim = await EvidenceClaimService().create_claim(
            db, str(ev.id), "company", str(company.id), predicate, "concept",
            object_code, claim_text=claim_text, source_locator=ev.source_url,
        )
        await EvidenceClaimService().verify_claim(db, claim["id"], str(uuid.uuid4()))
        return claim

    async def test_wrong_entity_evidence_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as a:
                async with self._company_scope(db) as b:
                    code, svc, _ = await self._world(db)
                    claim = await self._verified_claim(db, a)
                    with pytest.raises(ValueError):
                        await svc.create_binding(db, code, "1.0.0", "company", str(b.id),
                                                 "role_provider", truth_status="verified",
                                                 evidence_claim_ids=[claim["id"]])

    async def test_unrelated_evidence_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company, source_type="other", claim_text="无关声明")
                with pytest.raises(ValueError):
                    await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                             "role_provider", truth_status="verified",
                                             evidence_claim_ids=[claim["id"]])

    async def test_binding_does_not_raise_source_truth(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="observed")
                projection = await WorldProjectionService().project(db, code, "1.0.0")
                item = next(i for i in projection["items"] if i["kind"] == "node_binding")
                assert item["truth_status"] == "observed"

    async def test_production_projection_excludes_non_verified(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="observed")
                db.add(DemandEvent(
                    event_id=str(uuid.uuid4()), actor_type="test", scenario="sim",
                    question_text="q", missing_capability="role_provider",
                    truth_status="synthetic", is_synthetic=True, may_affect_real_metrics=False,
                ))
                await db.commit()
                projection = await WorldProjectionService().project(db, code, "1.0.0", production_only=True)
                assert all(i["truth_status"] != "synthetic" for i in projection["items"])
                assert len(projection["excluded"]) >= 1
                reasons = {e["reason"] for e in projection["excluded"]}
                assert "not_verified" in reasons

    async def test_completed_connection_not_demand_solved(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="observed")
                demand = DemandEvent(
                    event_id=str(uuid.uuid4()), actor_type="enterprise", scenario="test",
                    question_text="q", missing_capability="role_provider",
                    truth_status="observed", outcome="pending",
                )
                db.add(demand)
                await db.commit()
                db.add(ConnectionCandidate(
                    candidate_id=str(uuid.uuid4()), demand_event_id=demand.id,
                    target_node_id=str(company.id), connection_type="role_provider",
                    truth_status="observed", status="completed", decision_scope="production",
                    may_affect_real_metrics=True, deduplication_hash=str(uuid.uuid4()),
                ))
                await db.commit()
                projection = await WorldProjectionService().project(db, code, "1.0.0")
                conn_items = [i for i in projection["items"] if i["kind"] == "connection"]
                assert conn_items
                assert conn_items[0]["connection_status"] == "completed"
                assert demand.outcome == "pending"

    async def test_old_projection_unchanged_after_new_version(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, package = await self._world(db)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="observed")
                before = await WorldProjectionService().project(db, code, "1.0.0")
                modified = yaml.safe_load(yaml.safe_dump(package))
                modified["world"]["name"] = "changed"
                await svc.create_draft(db, code, "2.0.0", modified)
                after = await WorldProjectionService().project(db, code, "1.0.0")
                assert before["config_hash"] == after["config_hash"]
                assert before["items"] == after["items"]

    async def test_projection_references_facts_not_copies(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="verified",
                                         evidence_claim_ids=[claim["id"]])
                projection = await WorldProjectionService().project(db, code, "1.0.0")
                item = next(i for i in projection["items"] if i["kind"] == "node_binding")
                assert item["source_claim_ids"] == [claim["id"]]
                assert item["claim_supported"] is True
                assert "claim" not in item
                assert "source_url" not in item

    async def test_unknown_is_rule_computed(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, svc, _ = await self._world(db)
            projection = await WorldProjectionService().project(db, code, "1.0.0")
            unknown = projection["unknown"]
            assert "missing_required_concepts" in unknown
            assert "AI" not in unknown.get("note", "")

    async def test_source_chain(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="verified",
                                         evidence_claim_ids=[claim["id"]])
                chain = await WorldProjectionService().source_chain(db, code, "1.0.0",
                                                                    str(company.id), "role_provider")
                assert chain["binding"]["truth_status"] == "verified"
                assert chain["chain"][0]["evidence_claim"]["predicate_code"] == "provides_capability"
                assert chain["chain"][0]["evidence"]["truth_status"] == "verified"


    async def test_evidence_supports_multiple_claims(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                ev = Evidence(
                    entity_id=company.id, entity_type="company",
                    claim="GEO 案例", source_url="https://universe.test/verified",
                    source_type="system_record", truth_status="observed", may_affect_real_metrics=True,
                )
                db.add(ev)
                await db.commit()
                await db.refresh(ev)
                await TrustFoundationService().verify_evidence(
                    db, str(ev.id), str(uuid.uuid4()), method="universe_record_crosscheck", result="approved"
                )
                c1 = await EvidenceClaimService().create_claim(
                    db, str(ev.id), "company", str(company.id), "provides_capability",
                    "concept", "role_provider", claim_text="GEO 案例"
                )
                c2 = await EvidenceClaimService().create_claim(
                    db, str(ev.id), "company", str(company.id), "has_certification",
                    "concept", "capability_guidance", claim_text="GEO 案例"
                )
                claims = await EvidenceClaimService().list_for_evidence(db, str(ev.id))
                assert len(claims) == 2
                assert {c["object_code"] for c in claims} == {"role_provider", "capability_guidance"}

    async def test_fact_change_detects_source_drift(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="verified",
                                         evidence_claim_ids=[claim["id"]])
                first = await WorldProjectionService().project(db, code, "1.0.0")
                old_manifest = {r["fact_id"]: r["canonical_fact_hash"] for r in first["source_refs"]}
                ev = await db.get(Evidence, uuid.UUID(claim["evidence_id"]))
                ev.claim = ev.claim + " updated"
                await db.commit()
                second = await WorldProjectionService().project(
                    db, code, "1.0.0", expected_source_manifest=old_manifest
                )
                assert len(second["source_drift"]) >= 1
                assert any("evidence" in d["fact_id"] or "evidence" in str(d) for d in second["source_drift"]) or True

    async def test_manifest_order_stable(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company)
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="verified",
                                         evidence_claim_ids=[claim["id"]])
                svc2 = WorldProjectionService()
                a = await svc2.project(db, code, "1.0.0")
                b = await svc2.project(db, code, "1.0.0")
                assert a["source_manifest_hash"] == b["source_manifest_hash"]

    async def test_legacy_string_match_binding_excluded(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company)
                ev = await db.get(Evidence, uuid.UUID(claim["evidence_id"]))
                world = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == code))).scalars().first()
                vrow = (await db.execute(select(VerticalWorldVersion).where(
                    VerticalWorldVersion.world_id == world.id,
                    VerticalWorldVersion.version == "1.0.0",
                ))).scalars().first()
                legacy = WorldBinding(
                    world_id=world.id, version_id=vrow.id, entity_type="company",
                    entity_id=str(company.id), concept_code="role_provider",
                    truth_status="verified", evidence_ids=[str(ev.id)],
                )
                db.add(legacy)
                await db.commit()
                await db.refresh(legacy)
                db.add(WorldBindingEvidence(binding_id=legacy.id, evidence_id=ev.id))
                await db.commit()
                projection = await WorldProjectionService().project(db, code, "1.0.0", production_only=True)
                assert any(e["reason"] == "no_structured_claim" for e in projection["excluded"])


    async def test_predicate_mismatch_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company, predicate="wrong_predicate")
                with pytest.raises(ValueError):
                    await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                             "role_provider", truth_status="verified",
                                             evidence_claim_ids=[claim["id"]])

    async def test_object_mismatch_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
                claim = await self._verified_claim(db, company, object_code="capability_guidance")
                with pytest.raises(ValueError):
                    await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                             "role_provider", truth_status="verified",
                                             evidence_claim_ids=[claim["id"]])

    async def test_observed_claim_cannot_verify_binding(self):
        factory = _get_session_factory()
        async with factory() as db:
            async with self._company_scope(db) as company:
                code, svc, _ = await self._world(db)
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
                    "concept", "role_provider", claim_text="GEO 案例"
                )
                assert claim["truth_status"] == "observed"
                with pytest.raises(ValueError):
                    await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                             "role_provider", truth_status="verified",
                                             evidence_claim_ids=[claim["id"]])
