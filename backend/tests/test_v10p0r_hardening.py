"""V10-P0-R hardening tests: identity, authorization execution, outcome relevance."""

import sys
import uuid
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError

from app.database import _get_session_factory
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.models.company import Company
from app.models.brand import Brand
from app.models.product import Product
from app.models.governance import NodeMembership, AuditLog
from app.models.realm import RealmRegistry, RealmClaim, RealmDataAuthorization, RealmDataAsset
from app.models.relationship import Relationship
from app.models.evidence import Evidence
from app.models.evidence_claim import EvidenceClaim
from app.models.geo_project import (
    GeoProject,
    ProjectWorkItem,
    ProjectArtifact,
    ToolExecutionRecord,
    ProjectOutcome,
)
from app.models.reputation import Reputation
from app.models.reputation_event_record import ReputationEventRecord
from app.services.realm_service import get_realm_service
from app.services.geo_project_service import get_geo_project_service
from app.services.evidence_claim import get_evidence_claim_service
from app.services.trust_foundation import TrustFoundationService


def make_user(db, email, role=UserRole.ENTERPRISE):
    u = User(email=email, password_hash="x", name="用户", role=role)
    db.add(u)
    return u


async def _create_enterprise(db, user, name=None):
    svc = get_realm_service()
    ws = await svc.create_enterprise(db, user, {
        "name": name or f"V10R {uuid.uuid4().hex[:6]}",
        "website": f"https://{uuid.uuid4().hex[:8]}.test",
    })
    entity_id = uuid.UUID(ws["identity"]["id"])
    registry = (await db.execute(
        select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
    )).scalars().first()
    return entity_id, registry.id


async def _cleanup(db, entity_ids, user_ids):
    for eid in entity_ids:
        registry = (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == eid)
        )).scalars().first()
        if registry:
            projects = (await db.execute(
                select(GeoProject).where(GeoProject.realm_id == registry.id)
            )).scalars().all()
            for p in projects:
                await db.execute(delete(ProjectOutcome).where(ProjectOutcome.project_id == p.id))
                await db.execute(delete(ToolExecutionRecord).where(ToolExecutionRecord.project_id == p.id))
                await db.execute(delete(ProjectArtifact).where(ProjectArtifact.project_id == p.id))
                await db.execute(delete(ProjectWorkItem).where(ProjectWorkItem.project_id == p.id))
            await db.execute(delete(GeoProject).where(GeoProject.realm_id == registry.id))
        await db.execute(delete(RealmClaim).where(RealmClaim.entity_id == eid))
        await db.execute(delete(RealmDataAsset).where(RealmDataAsset.entity_id == eid))
        await db.execute(delete(RealmDataAuthorization).where(RealmDataAuthorization.entity_id == eid))
        await db.execute(delete(EvidenceClaim).where(EvidenceClaim.subject_id == str(eid)))
        await db.execute(delete(Evidence).where(Evidence.entity_id == eid))
        await db.execute(delete(Relationship).where(
            (Relationship.source_id == eid) | (Relationship.target_id == eid)
        ))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(eid)))
        await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == eid))
        await db.execute(delete(Brand).where(Brand.id == eid))
        await db.execute(delete(Product).where(Product.id == eid))
        await db.execute(delete(Company).where(Company.id == eid))
        await db.execute(delete(Entity).where(Entity.id == eid))
    for uid in user_ids:
        await db.execute(delete(User).where(User.id == uid))
    await db.commit()


async def _verified_relevant_claim(db, entity_id, project_id, artifact_id=None,
                                   predicate="appears_in_ai_answer", object_code="ai_answer_mention",
                                   claim_text="AI回答中出现品牌", metadata_project=True):
    ev = Evidence(
        entity_id=entity_id,
        entity_type="company",
        claim=claim_text,
        source_url=f"https://{uuid.uuid4().hex[:8]}.test",
        source_type="official_website",
        truth_status="observed",
        may_affect_real_metrics=False,
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    await TrustFoundationService().verify_evidence(
        db, str(ev.id), str(uuid.uuid4()),
        method="universe_record_crosscheck", result="approved"
    )
    metadata = {"project_id": str(project_id)} if metadata_project else {}
    if artifact_id:
        metadata["artifact_id"] = str(artifact_id)
    claim = await get_evidence_claim_service().create_claim(
        db, str(ev.id), "entity", str(entity_id), predicate,
        "concept", object_code, object_value=claim_text,
        claim_text=claim_text, metadata=metadata,
    )
    row = await db.get(EvidenceClaim, uuid.UUID(claim["id"]))
    row.may_affect_real_metrics = True
    await db.commit()
    await get_evidence_claim_service().verify_claim(
        db, claim["id"], str(uuid.uuid4()), method="structured_review", result="approved"
    )
    return claim, ev


class TestRealmIdentity:
    async def test_unified_entity_realm_id(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"unified-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            ent_id, _ = await _create_enterprise(db, user)
            brand = Brand(name="V10R品牌", entity_type="brand", geo_id=f"GEO-BRAND-{uuid.uuid4().hex[:8].upper()}")
            product = Product(name="V10R产品", entity_type="product", geo_id=f"GEO-PROD-{uuid.uuid4().hex[:8].upper()}")
            db.add_all([brand, product])
            await db.commit()
            await db.refresh(brand)
            await db.refresh(product)
            brand_id, product_id = brand.id, product.id
            user_id = user.id
            try:
                for obj, realm_type in ((brand, "brand"), (product, "product")):
                    db.add(RealmRegistry(
                        entity_id=obj.id,
                        entity_type=obj.entity_type,
                        realm_type=realm_type,
                        realm_code=f"R-{realm_type[:4].upper()}-{uuid.uuid4().hex[:10].upper()}",
                        display_name=obj.name,
                        lifecycle_state="registered",
                        claim_status="none",
                    ))
                await db.commit()
                ids = {ent_id, brand_id, product_id}
                assert len(ids) == 3
                for eid in ids:
                    reg = (await db.execute(
                        select(RealmRegistry).where(RealmRegistry.entity_id == eid)
                    )).scalars().first()
                    assert reg is not None
                    assert reg.entity_id == eid
                with pytest.raises(IntegrityError):
                    db.add(RealmRegistry(
                        entity_id=ent_id, entity_type="company", realm_type="enterprise",
                        realm_code=f"R-DUP-{uuid.uuid4().hex[:8]}", display_name="dup",
                        lifecycle_state="registered", claim_status="none",
                    ))
                    await db.commit()
                await db.rollback()
            finally:
                await _cleanup(db, [ent_id, brand_id, product_id], [user_id])

    async def test_claim_existing_requires_review_and_no_control(self):
        factory = _get_session_factory()
        async with factory() as db:
            claimant = make_user(db, f"claim-{uuid.uuid4().hex[:8]}@x.com")
            reviewer = make_user(db, f"review-{uuid.uuid4().hex[:8]}@x.com", UserRole.REVIEWER)
            db.add_all([claimant, reviewer])
            await db.commit()
            await db.refresh(claimant)
            await db.refresh(reviewer)
            legacy = Brand(name="已有品牌", entity_type="brand", geo_id=f"GEO-BRAND-{uuid.uuid4().hex[:8].upper()}")
            db.add(legacy)
            await db.commit()
            await db.refresh(legacy)
            try:
                svc = get_realm_service()
                result = await svc.claim(db, claimant, str(legacy.id), {"reason": "品牌方证明"})
                assert result["status"] == "pending"
                roles = await svc.list_mine(db, claimant)
                assert all(r["entity_id"] != str(legacy.id) for r in roles)
                memberships = (await db.execute(
                    select(NodeMembership).where(NodeMembership.node_id == str(legacy.id))
                )).scalars().all()
                assert not memberships
                registry = (await db.execute(
                    select(RealmRegistry).where(RealmRegistry.entity_id == legacy.id)
                )).scalars().first()
                assert registry.claim_status == "pending"
                decided = await svc.decide_claim(db, reviewer, result["claim_id"], "approved", reason="资料核对通过")
                assert decided["status"] == "approved"
                memberships = (await db.execute(
                    select(NodeMembership).where(NodeMembership.node_id == str(legacy.id))
                )).scalars().all()
                assert any(m.user_id == claimant.id and m.role == "node_owner" for m in memberships)
            finally:
                await _cleanup(db, [legacy.id], [claimant.id, reviewer.id])

    async def test_concurrent_claim_idempotent(self):
        factory = _get_session_factory()
        async with factory() as db:
            u1 = make_user(db, f"con1-{uuid.uuid4().hex[:8]}@x.com")
            u2 = make_user(db, f"con2-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([u1, u2])
            await db.commit()
            await db.refresh(u1)
            await db.refresh(u2)
            legacy = Brand(name="并发品牌", entity_type="brand", geo_id=f"GEO-BRAND-{uuid.uuid4().hex[:8].upper()}")
            db.add(legacy)
            await db.commit()
            await db.refresh(legacy)
            try:
                svc = get_realm_service()
                r1 = await svc.claim(db, u1, str(legacy.id))
                r2 = await svc.claim(db, u2, str(legacy.id))
                dup = await svc.claim(db, u1, str(legacy.id))
                assert dup["claim_id"] == r1["claim_id"]
                assert r2["status"] == "pending"
                count = (await db.execute(
                    select(func.count(RealmClaim.id)).where(RealmClaim.entity_id == legacy.id)
                )).scalar()
                assert count == 2
            finally:
                await _cleanup(db, [legacy.id], [u1.id, u2.id])


class TestAuthorizationExecution:
    async def _project(self, db, user):
        entity_id, registry_id = await _create_enterprise(db, user)
        project = await get_geo_project_service().create_project(db, user, {
            "realm_id": str(registry_id), "name": "授权项目",
        })
        return entity_id, registry_id, project

    async def test_tool_execution_requires_and_validates_authorization(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"authz-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await self._project(db, user)
            svc = get_geo_project_service()
            try:
                with pytest.raises(ValueError):
                    await svc.create_tool_execution(db, user, project["id"], {
                        "provider": "universe", "tool_name": "geo_visibility",
                    })
                auth = await get_realm_service().create_authorization(db, user, str(entity_id), {
                    "source_name": "官网", "use_scope": "ai_tools",
                    "grantee_type": "provider", "provider": "universe", "tool_name": "geo_visibility",
                })
                run = await svc.create_tool_execution(db, user, project["id"], {
                    "provider": "universe", "tool_name": "geo_visibility",
                    "authorization_id": auth["id"],
                })
                assert run["execution_source"] == "declared"
                assert run["execution_status"] == "declared"
                assert run["authorization_hash"]
                await get_realm_service().revoke_authorization(db, user, str(entity_id), auth["id"], reason="test")
                with pytest.raises(ValueError):
                    await svc.create_tool_execution(db, user, project["id"], {
                        "provider": "universe", "tool_name": "geo_visibility",
                        "authorization_id": auth["id"],
                    })
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_external_provider_scope_and_expiry_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"ext-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await self._project(db, user)
            svc = get_geo_project_service()
            rs = get_realm_service()
            try:
                bad_scope = await rs.create_authorization(db, user, str(entity_id), {
                    "use_scope": "project_evidence", "grantee_type": "provider",
                    "provider": "openai", "tool_name": "chat",
                })
                with pytest.raises(ValueError):
                    await svc.create_tool_execution(db, user, project["id"], {
                        "provider": "openai", "tool_name": "chat",
                        "authorization_id": bad_scope["id"],
                    })
                external_ok = await rs.create_authorization(db, user, str(entity_id), {
                    "use_scope": "ai_tools", "grantee_type": "provider",
                    "provider": "openai", "tool_name": "chat",
                    "allow_external_processing": True,
                })
                check = await rs.validate_authorization(db, external_ok["id"], provider="openai", tool_name="chat")
                assert check["valid"] is True
                expired = await rs.create_authorization(db, user, str(entity_id), {
                    "use_scope": "ai_tools", "grantee_type": "provider",
                    "provider": "universe", "tool_name": "geo_visibility",
                    "valid_until": "2020-01-01T00:00:00Z",
                })
                with pytest.raises(ValueError):
                    await svc.create_tool_execution(db, user, project["id"], {
                        "provider": "universe", "tool_name": "geo_visibility",
                        "authorization_id": expired["id"],
                    })
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_observed_never_enters_real_metrics(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"obs-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await self._project(db, user)
            rs = get_realm_service()
            try:
                auth = await rs.create_authorization(db, user, str(entity_id), {
                    "use_scope": "project_evidence", "source_name": "官网",
                })
                asset = await rs.create_asset(db, user, str(entity_id), {
                    "asset_key": "obs-key", "title": "观察资料",
                    "authorization_id": auth["id"], "truth_status": "observed",
                })
                assert asset["may_affect_real_metrics"] is False
                ev = await rs.create_evidence(db, user, str(entity_id), {
                    "claim": "观察证据", "source_url": "https://x.test",
                    "authorization_id": auth["id"], "truth_status": "observed",
                })
                assert ev["may_affect_real_metrics"] is False
                with pytest.raises(ValueError):
                    await rs.create_evidence(db, user, str(entity_id), {
                        "claim": "伪造", "source_url": "https://x.test", "truth_status": "verified",
                    })
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_cross_realm_read_and_create_blocked(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"cross-owner-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"cross-out-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, registry_id, project = await self._project(db, owner)
            svc = get_geo_project_service()
            try:
                with pytest.raises(PermissionError):
                    await svc.get_project(db, outsider, project["id"])
                with pytest.raises(PermissionError):
                    await svc.timeline(db, outsider, project["id"])
                with pytest.raises(PermissionError):
                    await svc.create_work_item(db, outsider, project["id"], {
                        "work_type": "diagnosis", "title": "越权",
                    })
            finally:
                await _cleanup(db, [entity_id], [owner.id, outsider.id])


class TestOutcomeRelevance:
    async def _project(self, db, user):
        entity_id, registry_id = await _create_enterprise(db, user)
        project = await get_geo_project_service().create_project(db, user, {
            "realm_id": str(registry_id), "name": "结果项目",
        })
        return entity_id, registry_id, project

    async def test_unrelated_verified_claim_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"rel-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await self._project(db, user)
            svc = get_geo_project_service()
            try:
                claim, _ = await _verified_relevant_claim(
                    db, entity_id, project["id"],
                    predicate="has_capability", object_code="education_tech_planning",
                    claim_text="官网证明规划能力", metadata_project=False,
                )
                with pytest.raises(ValueError):
                    await svc.create_outcome(db, user, project["id"], {
                        "outcome_type": "visibility_observation",
                        "claim_text": "AI回答中出现品牌",
                        "evidence_claim_id": claim["id"],
                    })
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_verified_relevant_outcome_and_revocation_refresh(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"out-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await self._project(db, user)
            svc = get_geo_project_service()
            try:
                claim, ev = await _verified_relevant_claim(
                    db, entity_id, project["id"],
                    artifact_id=str(uuid.uuid4()),
                )
                outcome = await svc.create_outcome(db, user, project["id"], {
                    "outcome_type": "visibility_observation",
                    "claim_text": "AI回答中出现品牌",
                    "evidence_claim_id": claim["id"],
                })
                assert outcome["status"] == "verified"
                assert outcome["truth_status"] == "verified"
                assert outcome["validation_config_version"] == "1.1.0"
                claim_row = await db.get(EvidenceClaim, uuid.UUID(claim["id"]))
                claim_row.truth_status = "revoked"
                await db.commit()
                refreshed = await svc.refresh_outcome(db, user, outcome["id"])
                assert refreshed["status"] == "revoked"
                assert refreshed["truth_status"] == "observed"
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_project_and_outcome_do_not_change_reputation(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"rep-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await self._project(db, user)
            svc = get_geo_project_service()
            try:
                rep_before = (await db.execute(
                    select(func.count(Reputation.id)).where(Reputation.node_id == entity_id)
                )).scalar() or 0
                events_before = (await db.execute(
                    select(func.count(ReputationEventRecord.event_id)).where(ReputationEventRecord.node_id == str(entity_id))
                )).scalar() or 0
                auth = await get_realm_service().create_authorization(db, user, str(entity_id), {
                    "use_scope": "ai_tools", "grantee_type": "provider",
                    "provider": "universe", "tool_name": "geo_visibility",
                })
                await svc.create_tool_execution(db, user, project["id"], {
                    "provider": "universe", "tool_name": "geo_visibility",
                    "authorization_id": auth["id"],
                })
                await svc.create_outcome(db, user, project["id"], {
                    "outcome_type": "visibility_observation", "claim_text": "观察声明",
                })
                rep_after = (await db.execute(
                    select(func.count(Reputation.id)).where(Reputation.node_id == entity_id)
                )).scalar() or 0
                events_after = (await db.execute(
                    select(func.count(ReputationEventRecord.event_id)).where(ReputationEventRecord.node_id == str(entity_id))
                )).scalar() or 0
                assert rep_after == rep_before
                assert events_after == events_before
            finally:
                await _cleanup(db, [entity_id], [user.id])


class TestLocalRealTool:
    async def test_system_execution_source_local_adapter(self):
        factory = _get_session_factory()
        async with factory() as db:
            reviewer = make_user(db, f"sys-{uuid.uuid4().hex[:8]}@x.com", UserRole.REVIEWER)
            db.add(reviewer)
            await db.commit()
            await db.refresh(reviewer)
            entity_id, registry_id = await _create_enterprise(db, reviewer)
            project = await get_geo_project_service().create_project(db, reviewer, {
                "realm_id": str(registry_id), "name": "本地工具项目",
                "target_brand": "V10R教育", "question_set": ["科技特长生如何规划"],
            })
            try:
                auth = await get_realm_service().create_authorization(db, reviewer, str(entity_id), {
                    "use_scope": "ai_tools", "grantee_type": "provider",
                    "provider": "universe", "tool_name": "geo_visibility",
                })
                run = await get_geo_project_service().run_local_tool(db, reviewer, project["id"], {
                    "authorization_id": auth["id"], "tool_name": "geo_visibility",
                })
                assert run["execution_source"] == "system"
                assert run["execution_status"] == "success"
                assert run["provider"] == "universe"
                assert run["output_manifest"]["data_origin"] == "local_real"
            finally:
                await _cleanup(db, [entity_id], [reviewer.id])
