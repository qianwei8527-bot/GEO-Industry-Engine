"""V10-P1 operations tests: publish, monitoring, summary, review queues."""

import sys
import uuid
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select, delete

from app.database import _get_session_factory
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.models.company import Company
from app.models.brand import Brand
from app.models.product import Product
from app.models.governance import NodeMembership
from app.models.realm import RealmRegistry, RealmClaim, RealmDataAuthorization, RealmDataAsset
from app.models.relationship import Relationship
from app.models.evidence import Evidence
from app.models.evidence_claim import EvidenceClaim
from app.models.geo_project import GeoProject, ProjectWorkItem, ProjectArtifact, ToolExecutionRecord, ProjectOutcome
from app.services.realm_service import get_realm_service
from app.services.geo_project_service import get_geo_project_service


def make_user(db, email, role=UserRole.ENTERPRISE):
    u = User(email=email, password_hash="x", name="用户", role=role)
    db.add(u)
    return u


async def _setup(db, user):
    ws = await get_realm_service().create_enterprise(db, user, {
        "name": f"P1 {uuid.uuid4().hex[:6]}",
        "website": f"https://{uuid.uuid4().hex[:8]}.test",
    })
    entity_id = uuid.UUID(ws["identity"]["id"])
    registry = (await db.execute(
        select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
    )).scalars().first()
    project = await get_geo_project_service().create_project(db, user, {
        "realm_id": str(registry.id), "name": "P1运营项目",
    })
    return entity_id, registry.id, project


async def _cleanup(db, entity_ids, user_ids):
    for eid in entity_ids:
        registry = (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == eid)
        )).scalars().first()
        if registry:
            projects = (await db.execute(select(GeoProject).where(GeoProject.realm_id == registry.id))).scalars().all()
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
        await db.execute(delete(Relationship).where((Relationship.source_id == eid) | (Relationship.target_id == eid)))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(eid)))
        await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == eid))
        await db.execute(delete(Brand).where(Brand.id == eid))
        await db.execute(delete(Product).where(Product.id == eid))
        await db.execute(delete(Company).where(Company.id == eid))
        await db.execute(delete(Entity).where(Entity.id == eid))
    for uid in user_ids:
        await db.execute(delete(User).where(User.id == uid))
    await db.commit()


class TestOperations:
    async def test_publish_monitoring_summary(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"p1-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await _setup(db, user)
            svc = get_geo_project_service()
            try:
                artifact = await svc.create_artifact(db, user, project["id"], {
                    "artifact_type": "report", "title": "试点报告", "content_text": "真实报告草稿",
                })
                published = await svc.publish_artifact(db, user, artifact["id"], {
                    "published_url": "https://example.com/p1",
                    "delivery_recipient": "客户A",
                })
                assert published["status"] == "published"
                assert published["content_hash"]
                monitor = await svc.record_monitoring_result(db, user, project["id"], {
                    "metric_key": "mention_rate", "metric_value": 0.42,
                    "raw_result_ref": "https://example.com/obs",
                })
                assert monitor["status"] == "observed"
                assert monitor["metric_key"] == "mention_rate"
                summary = await svc.project_summary(db, user, project["id"])
                assert summary["artifacts"]["published"] == 1
                assert summary["monitoring_results"] == 1
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_non_member_cannot_publish_or_monitor(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"p1o-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"p1x-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, registry_id, project = await _setup(db, owner)
            svc = get_geo_project_service()
            try:
                artifact = await svc.create_artifact(db, owner, project["id"], {
                    "artifact_type": "report", "title": "越权产物",
                })
                with pytest.raises(PermissionError):
                    await svc.publish_artifact(db, outsider, artifact["id"], {})
                with pytest.raises(PermissionError):
                    await svc.record_monitoring_result(db, outsider, project["id"], {
                        "metric_key": "mention_rate", "metric_value": 0.1,
                    })
            finally:
                await _cleanup(db, [entity_id], [owner.id, outsider.id])

    async def test_review_queues_require_reviewer(self):
        factory = _get_session_factory()
        async with factory() as db:
            plain = make_user(db, f"p1q-{uuid.uuid4().hex[:8]}@x.com")
            reviewer = make_user(db, f"p1r-{uuid.uuid4().hex[:8]}@x.com", UserRole.REVIEWER)
            db.add_all([plain, reviewer])
            await db.commit()
            await db.refresh(plain)
            await db.refresh(reviewer)
            try:
                with pytest.raises(PermissionError):
                    await get_realm_service().list_claims(db, plain, "pending")
                claims = await get_realm_service().list_claims(db, reviewer, "pending")
                assert isinstance(claims, list)
                from app.services.evidence_claim import get_evidence_claim_service
                observed_claims = await get_evidence_claim_service().list_review(db, "observed", 5)
                assert isinstance(observed_claims, list)
            finally:
                await _cleanup(db, [], [plain.id, reviewer.id])

    async def test_publish_monitoring_url_safety(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"p1u-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project = await _setup(db, user)
            svc = get_geo_project_service()
            try:
                artifact = await svc.create_artifact(db, user, project["id"], {
                    "artifact_type": "report", "title": "安全产物",
                })
                with pytest.raises(ValueError):
                    await svc.publish_artifact(db, user, artifact["id"], {
                        "published_url": "ftp://example.com",
                    })
                with pytest.raises(ValueError):
                    await svc.record_monitoring_result(db, user, project["id"], {
                        "metric_key": "mention_rate", "metric_value": 0.1,
                        "raw_result_ref": "https://192.168.1.1/obs",
                    })
            finally:
                await _cleanup(db, [entity_id], [user.id])
