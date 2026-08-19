"""V10.1 Sixth Business Module capability tests."""

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
from app.models.capability_definition import CapabilityDefinition
from app.services.realm_service import get_realm_service
from app.services.geo_project_service import get_geo_project_service
from app.services.capability_service import get_capability_service


def make_user(db, email, role=UserRole.ENTERPRISE):
    u = User(email=email, password_hash="x", name="用户", role=role)
    db.add(u)
    return u


async def _setup(db, user):
    ws = await get_realm_service().create_enterprise(db, user, {
        "name": f"CAP {uuid.uuid4().hex[:6]}",
        "website": f"https://{uuid.uuid4().hex[:8]}.test",
    })
    entity_id = uuid.UUID(ws["identity"]["id"])
    registry = (await db.execute(
        select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
    )).scalars().first()
    project = await get_geo_project_service().create_project(db, user, {
        "realm_id": str(registry.id), "name": "能力项目",
        "target_brand": "V10教育", "question_set": ["科技特长生如何规划"],
    })
    auth = await get_realm_service().create_authorization(db, user, str(entity_id), {
        "source_name": "官网", "use_scope": "ai_tools",
        "grantee_type": "provider", "provider": "universe", "tool_name": "geo_visibility",
    })
    return entity_id, registry.id, project, auth


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
        await db.execute(delete(CapabilityDefinition).where(CapabilityDefinition.realm_entity_id == eid))
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


class TestCapabilityModule:
    async def test_list_three_source_modes_and_create_realm_owner(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"cap-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project, auth = await _setup(db, user)
            svc = get_capability_service()
            try:
                caps = await svc.list(db, user, realm_entity_id=str(entity_id))
                assert any(c["capability_id"] == "geo_visibility" for c in caps)
                external = next(c for c in caps if c["capability_id"] == "external_chatgpt")
                assert external["available"] is False
                created = await svc.create(db, user, {
                    "realm_entity_id": str(entity_id),
                    "name": "域主问题整理器",
                    "capability_type": "growth_skill_workflow",
                    "tool_name": "issue_collector",
                })
                assert created["source_mode"] == "realm_owner"
                assert created["status"] == "draft"
                listed = await svc.list(db, user, source_mode="realm_owner", realm_entity_id=str(entity_id))
                assert any(c["capability_id"] == created["capability_id"] for c in listed)
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_platform_system_run_and_external_declared_run(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"run-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, registry_id, project, auth = await _setup(db, user)
            svc = get_capability_service()
            try:
                system_run = await svc.run(db, user, "geo_visibility", {
                    "project_id": project["id"],
                    "authorization_id": auth["id"],
                })
                assert system_run["execution_source"] == "system"
                assert system_run["execution_status"] == "success"
                assert system_run["source_mode"] == "platform_standard"
                assert system_run["capability_id"] == "geo_visibility"
                external_auth = await get_realm_service().create_authorization(db, user, str(entity_id), {
                    "source_name": "外部人工观察", "use_scope": "ai_tools",
                    "grantee_type": "provider", "provider": "openai", "tool_name": "chatgpt",
                    "allow_external_processing": True,
                })
                external_run = await svc.run(db, user, "external_chatgpt", {
                    "project_id": project["id"],
                    "authorization_id": external_auth["id"],
                    "output_manifest": {"question": "科技特长生如何规划", "answer": "人工观察结果"},
                })
                assert external_run["execution_source"] == "declared"
                assert external_run["truth_status"] == "observed"
                assert external_run["source_mode"] == "external_connected"
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_outsider_cannot_run_or_list_private(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"capo-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"capx-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, registry_id, project, auth = await _setup(db, owner)
            svc = get_capability_service()
            try:
                created = await svc.create(db, owner, {
                    "realm_entity_id": str(entity_id),
                    "name": "私有能力",
                    "capability_type": "tool_connector",
                })
                with pytest.raises(PermissionError):
                    await svc.get(db, outsider, created["capability_id"])
                with pytest.raises(PermissionError):
                    await svc.run(db, outsider, "geo_visibility", {
                        "project_id": project["id"],
                        "authorization_id": auth["id"],
                    })
                with pytest.raises(ValueError):
                    await svc.create(db, owner, {
                        "realm_entity_id": str(entity_id),
                        "name": "越权模式",
                        "capability_type": "geo_agent",
                        "source_mode": "platform_standard",
                    })
            finally:
                await _cleanup(db, [entity_id], [owner.id, outsider.id])
