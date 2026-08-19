"""V10-P0 Realm owner protocol tests."""

import sys
import uuid
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select, delete

from app.database import _get_session_factory
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.models.brand import Brand
from app.models.company import Company
from app.models.governance import NodeMembership
from app.models.realm import RealmRegistry, RealmClaim, RealmDataAuthorization, RealmDataAsset
from app.models.relationship import Relationship
from app.models.evidence import Evidence
from app.models.geo_project import GeoProject
from app.services.realm_service import get_realm_service


def make_user(db, email, role=UserRole.ENTERPRISE):
    u = User(email=email, password_hash="x", name="域主", role=role)
    db.add(u)
    return u


async def _cleanup(db, entity_ids, user_ids):
    for eid in entity_ids:
        await db.execute(delete(RealmClaim).where(RealmClaim.entity_id == eid))
        await db.execute(delete(RealmDataAsset).where(RealmDataAsset.entity_id == eid))
        await db.execute(delete(RealmDataAuthorization).where(RealmDataAuthorization.entity_id == eid))
        await db.execute(delete(Evidence).where(Evidence.entity_id == eid))
        await db.execute(delete(Relationship).where(
            (Relationship.source_id == eid) | (Relationship.target_id == eid)
        ))
        await db.execute(delete(GeoProject).where(GeoProject.realm_entity_id == eid))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(eid)))
        await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == eid))
        await db.execute(delete(Brand).where(Brand.id == eid))
        await db.execute(delete(Company).where(Company.id == eid))
        await db.execute(delete(Entity).where(Entity.id == eid))
    for uid in user_ids:
        await db.execute(delete(User).where(User.id == uid))
    await db.commit()


class TestRealmOwner:
    async def test_enterprise_realm_creation_and_control(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"realm-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            svc = get_realm_service()
            ws = await svc.create_enterprise(db, user, {
                "name": "V10 教育科技",
                "website": f"https://{uuid.uuid4().hex[:8]}.test",
                "description": "V10-P0 fixture",
            })
            entity_id = uuid.UUID(ws["identity"]["id"])
            try:
                assert ws["realm"]["realm_type"] == "enterprise"
                assert ws["realm"]["lifecycle_state"] == "claimed"
                assert ws["access"]["controlled"] is True
                assert ws["access"]["can_verify"] is False
                registry = (await db.execute(
                    select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
                )).scalars().first()
                assert registry is not None
                assert registry.owner_id == user.id
                membership = (await db.execute(
                    select(NodeMembership).where(
                        NodeMembership.user_id == user.id,
                        NodeMembership.node_id == str(entity_id),
                    )
                )).scalars().first()
                assert membership is not None and membership.role == "node_owner"
            finally:
                await _cleanup(db, [entity_id], [user.id])

    async def test_brand_realm_and_claim_boundary(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"brand-owner-{uuid.uuid4().hex[:8]}@x.com")
            other = make_user(db, f"brand-other-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, other])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(other)
            svc = get_realm_service()
            ws = await svc.create_brand(db, owner, {"name": "V10 品牌"})
            entity_id = uuid.UUID(ws["identity"]["id"])
            try:
                assert ws["realm"]["realm_type"] == "brand"
                mine = await svc.list_mine(db, owner)
                assert any(r["entity_id"] == str(entity_id) for r in mine)
                result = await svc.claim(db, other, str(entity_id), {"reason": "品牌方"})
                assert result["status"] == "pending"
                boundary = await svc.boundary(db)
                assert boundary["realms"] >= 1
            finally:
                await _cleanup(db, [entity_id], [owner.id, other.id])

    async def test_data_authorization_asset_and_evidence_do_not_fabricate(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"data-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            svc = get_realm_service()
            ws = await svc.create_enterprise(db, user, {
                "name": "V10 数据域", "website": f"https://{uuid.uuid4().hex[:8]}.test"
            })
            entity_id = ws["identity"]["id"]
            try:
                auth = await svc.create_authorization(db, user, entity_id, {
                    "source_name": "官网", "source_url": "https://a.test",
                    "source_type": "official_website", "license": "realm-owner",
                    "use_scope": "project_evidence",
                })
                assert auth["truth_status"] == "observed"
                assert auth["may_affect_real_metrics"] is False
                asset = await svc.create_asset(db, user, entity_id, {
                    "asset_key": "brand-brief", "title": "品牌资料",
                    "asset_type": "document", "authorization_id": auth["id"],
                })
                duplicate = await svc.create_asset(db, user, entity_id, {
                    "asset_key": "brand-brief", "title": "品牌资料",
                    "asset_type": "document", "authorization_id": auth["id"],
                })
                assert duplicate["id"] == asset["id"]
                ev = await svc.create_evidence(db, user, entity_id, {
                    "claim": "官网发布品牌资料", "source_url": "https://a.test",
                    "source_type": "official_website", "authorization_id": auth["id"],
                })
                assert ev["truth_status"] == "observed"
                assert ev["may_affect_real_metrics"] is False
                with pytest.raises(ValueError):
                    await svc.create_evidence(db, user, entity_id, {
                        "claim": "伪造验证", "source_url": "https://a.test",
                        "truth_status": "verified",
                    })
            finally:
                await _cleanup(db, [uuid.UUID(entity_id)], [user.id])

    async def test_realm_relationship_requires_control(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"rel-owner-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"rel-out-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            svc = get_realm_service()
            ws = await svc.create_enterprise(db, owner, {
                "name": "V10 关系域", "website": f"https://{uuid.uuid4().hex[:8]}.test"
            })
            entity_id = uuid.UUID(ws["identity"]["id"])
            target = Brand(name="目标品牌", entity_type="brand", geo_id=f"GEO-BRAND-{uuid.uuid4().hex[:8].upper()}")
            db.add(target)
            await db.commit()
            await db.refresh(target)
            try:
                rel = await svc.add_relationship(db, owner, str(entity_id), {
                    "target_id": str(target.id), "relation_type": "partner",
                    "description": "品牌合作",
                })
                assert rel["relation_type"] == "partner"
                with pytest.raises(PermissionError):
                    await svc.add_relationship(db, outsider, str(entity_id), {
                        "target_id": str(target.id), "relation_type": "partner",
                    })
            finally:
                await _cleanup(db, [entity_id, target.id], [owner.id, outsider.id])
