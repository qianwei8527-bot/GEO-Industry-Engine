"""V10-P0 Realm owner service.

Realm = product-level term for the legacy Entity/Node compatibility layer.
This service handles realm creation, claiming, data authorization/import,
relationship creation and the realm workspace projection.
"""

import hashlib
import json
import os
import secrets
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import yaml
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity
from app.models.brand import Brand
from app.models.company import Company
from app.models.governance import NodeMembership
from app.models.realm import (
    RealmRegistry,
    RealmClaim,
    RealmDataAuthorization,
    RealmDataAsset,
)
from app.models.relationship import Relationship
from app.models.evidence import Evidence
from app.models.evidence_claim import EvidenceClaim
from app.models.geo_project import GeoProject, ProjectOutcome, ProjectArtifact
from app.services.governance import get_governance_service


def _load_realm_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "config", "universe", "realm_governance.yaml",
    )
    if os.path.exists(p):
        raw = open(p, encoding="utf-8").read()
        data = yaml.safe_load(raw) or {}
        data["config_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return data
    return {"version": "1.0.0", "config_hash": "missing"}


class RealmService:
    def __init__(self):
        self.config = _load_realm_config()

    async def _control(self, db: AsyncSession, user, entity_id: str) -> bool:
        gov = get_governance_service()
        if gov.is_system_admin(user):
            return True
        roles = await gov.get_node_roles(db, user.id, entity_id)
        allowed = set(self.config.get("permissions", {}).get("owner_roles", ["node_owner", "node_editor"]))
        return bool(set(roles) & allowed)

    async def _can_read(self, db: AsyncSession, user, entity_id: str) -> bool:
        gov = get_governance_service()
        if gov.is_system_admin(user):
            return True
        roles = await gov.get_node_roles(db, user.id, entity_id)
        return bool(roles)

    async def _audit(self, db, user, action: str, target_type: str, target_id: str, reason: str = None, metadata: Dict = None):
        gov = get_governance_service()
        await gov.audit(db, user.id, action, target_type, target_id, reason=reason,
                        actor_label=user.name, metadata=metadata)

    async def _registry(self, db, entity_id: str) -> Optional[RealmRegistry]:
        return (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == uuid.UUID(str(entity_id)))
        )).scalars().first()

    async def resolve_registry(self, db, realm_ref: str) -> Optional[RealmRegistry]:
        try:
            value = uuid.UUID(str(realm_ref))
        except (ValueError, TypeError):
            return None
        registry = await db.get(RealmRegistry, value)
        if registry:
            return registry
        return (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == value)
        )).scalars().first()

    async def create_enterprise(self, db: AsyncSession, user, data: Dict) -> Dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        if data.get("website"):
            exists = (await db.execute(
                select(Company).where(Company.website == data.get("website"))
            )).scalars().first()
            if exists and exists.owner_id and str(exists.owner_id) != str(user.id):
                raise ValueError("website is already controlled by another owner")
        company = Company(
            name=name,
            description=data.get("description"),
            website=data.get("website"),
            company_size=data.get("company_size"),
            industry_id=uuid.UUID(str(data["industry_id"])) if data.get("industry_id") else None,
            contact_email=data.get("contact_email"),
            entity_type="company",
            geo_id=f"GEO-COMP-{uuid.uuid4().hex[:10].upper()}",
            owner_id=user.id,
            region=data.get("region"),
        )
        db.add(company)
        await db.flush()
        await db.refresh(company)
        registry = RealmRegistry(
            entity_id=company.id,
            entity_type="company",
            realm_type="enterprise",
            realm_code=f"R-ENTR-{uuid.uuid4().hex[:10].upper()}",
            display_name=name,
            lifecycle_state="claimed",
            claim_status="approved",
            owner_id=user.id,
            source="realm_owner",
        )
        db.add(registry)
        await db.flush()
        await self._upsert_owner_membership(db, user.id, str(company.id), "company", user.id)
        await db.commit()
        await db.refresh(registry)
        await self._audit(db, user, "realm_created", "entity", str(company.id),
                          reason=f"enterprise realm {registry.realm_code}")
        return await self.get_workspace(db, user, str(company.id))

    async def create_brand(self, db: AsyncSession, user, data: Dict) -> Dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        entity = Brand(
            name=name,
            entity_type="brand",
            description=data.get("description"),
            geo_id=f"GEO-BRAND-{uuid.uuid4().hex[:10].upper()}",
            region=data.get("region"),
        )
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        registry = RealmRegistry(
            entity_id=entity.id,
            entity_type="brand",
            realm_type="brand",
            realm_code=f"R-BRAN-{uuid.uuid4().hex[:10].upper()}",
            display_name=name,
            lifecycle_state="claimed",
            claim_status="approved",
            owner_id=user.id,
            source="realm_owner",
        )
        db.add(registry)
        await db.flush()
        await self._upsert_owner_membership(db, user.id, str(entity.id), "brand", user.id)
        await db.commit()
        await db.refresh(registry)
        await self._audit(db, user, "realm_created", "entity", str(entity.id),
                          reason=f"brand realm {registry.realm_code}")
        return await self.get_workspace(db, user, str(entity.id))

    async def _upsert_owner_membership(self, db, user_id, node_id: str, node_type: str, actor_id) -> NodeMembership:
        row = (await db.execute(
            select(NodeMembership).where(
                NodeMembership.user_id == user_id,
                NodeMembership.node_id == node_id,
                NodeMembership.status == "active",
            )
        )).scalars().first()
        if row:
            row.role = "node_owner"
            row.node_type = node_type
            return row
        membership = NodeMembership(
            user_id=uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id,
            node_id=node_id,
            node_type=node_type,
            role="node_owner",
            status="active",
            created_by=actor_id,
            accepted_at=datetime.now(timezone.utc),
        )
        db.add(membership)
        return membership

    async def _register(self, db, entity_id, entity_type, realm_type, display_name,
                        owner_id, source="realm_owner") -> RealmRegistry:
        existing = await self._registry(db, entity_id)
        if existing:
            existing.display_name = display_name
            existing.owner_id = owner_id
            existing.lifecycle_state = "claimed"
            existing.claim_status = "approved"
            await db.commit()
            await db.refresh(existing)
            return existing
        registry = RealmRegistry(
            entity_id=entity_id,
            entity_type=entity_type,
            realm_type=realm_type,
            realm_code=f"R-{realm_type[:4].upper()}-{uuid.uuid4().hex[:10].upper()}",
            display_name=display_name,
            lifecycle_state="claimed",
            claim_status="approved",
            owner_id=owner_id,
            source=source,
        )
        db.add(registry)
        await db.commit()
        await db.refresh(registry)
        return registry

    async def claim(self, db: AsyncSession, user, entity_id: str, data: Dict = None) -> Dict:
        try:
            entity = await db.get(Entity, uuid.UUID(str(entity_id)))
        except (ValueError, TypeError):
            raise ValueError("entity_id must be a valid UUID")
        if not entity:
            raise ValueError("entity not found")
        reason = (data or {}).get("reason")
        existing = await self._registry(db, entity_id)
        gov = get_governance_service()
        if existing and existing.owner_id and str(existing.owner_id) == str(user.id):
            roles = await gov.get_node_roles(db, user.id, entity_id)
            if "node_owner" in roles:
                return {"status": "approved", "realm": existing.realm_code}

        dedup = hashlib.sha256(
            f"{entity_id}|{user.id}|claim".encode("utf-8")
        ).hexdigest()
        prior = (await db.execute(
            select(RealmClaim).where(RealmClaim.deduplication_hash == dedup)
        )).scalars().first()
        if prior:
            if prior.status in ("pending", "approved"):
                return {"status": prior.status, "claim_id": str(prior.id)}
            prior.status = "pending"
            prior.reason = reason
            prior.decided_by = None
            prior.decided_at = None
            prior.decided_reason = None
            await db.commit()
            await db.refresh(prior)
            return {"status": "pending", "claim_id": str(prior.id), "message": "claim resubmitted for governance review"}

        if not existing:
            realm_type = {"company": "enterprise", "brand": "brand", "product": "product"}.get(
                entity.entity_type, "enterprise"
            )
            registry = RealmRegistry(
                entity_id=entity.id,
                entity_type=entity.entity_type,
                realm_type=realm_type,
                realm_code=f"R-{realm_type[:4].upper()}-{uuid.uuid4().hex[:10].upper()}",
                display_name=entity.name,
                lifecycle_state="registered",
                claim_status="pending",
                source="realm_claim",
            )
            db.add(registry)
            await db.commit()
            await db.refresh(registry)
        else:
            existing.claim_status = "pending"
            existing.lifecycle_state = "registered"
            await db.commit()

        claim = RealmClaim(
            entity_id=entity.id,
            claimant_id=user.id,
            claim_type="claim",
            status="pending",
            reason=reason,
            deduplication_hash=dedup,
        )
        db.add(claim)
        await db.commit()
        await db.refresh(claim)
        await self._audit(db, user, "realm_claim_pending", "entity", entity_id,
                          reason="existing realm requires governance review")
        return {"status": "pending", "claim_id": str(claim.id), "message": "claim submitted for governance review"}

    async def decide_claim(self, db: AsyncSession, actor, claim_id: str, decision: str,
                           reason: str = None, force: bool = False) -> Dict:
        gov = get_governance_service()
        if not gov.is_reviewer(actor) and not gov.has_platform_action(actor, "manage_membership"):
            raise PermissionError("reviewer/admin permission required")
        try:
            claim = await db.get(RealmClaim, uuid.UUID(str(claim_id)))
        except (ValueError, TypeError):
            raise ValueError("claim_id must be a valid UUID")
        if not claim:
            raise ValueError("realm claim not found")
        if claim.status != "pending":
            raise ValueError(f"claim already decided: {claim.status}")
        if decision not in ("approved", "rejected"):
            raise ValueError("decision must be approved/rejected")

        entity = await db.get(Entity, claim.entity_id)
        registry = await self._registry(db, claim.entity_id)
        if not registry:
            raise ValueError("realm registry not found")

        if decision == "approved":
            owners = (await db.execute(
                select(NodeMembership).where(
                    NodeMembership.node_id == str(claim.entity_id),
                    NodeMembership.role == "node_owner",
                    NodeMembership.status == "active",
                )
            )).scalars().all()
            existing_owner_ids = {str(m.user_id) for m in owners}
            if existing_owner_ids and str(claim.claimant_id) not in existing_owner_ids:
                if not force or not gov.is_system_admin(actor):
                    raise ValueError("realm already has an active owner; force transfer requires system_admin")
                for m in owners:
                    m.status = "revoked"
                    m.revoked_at = datetime.now(timezone.utc)
            await self._upsert_owner_membership(
                db, claim.claimant_id, str(claim.entity_id),
                entity.entity_type if entity else "realm", actor.id
            )
            registry.owner_id = claim.claimant_id
            registry.lifecycle_state = "claimed"
            registry.claim_status = "approved"
            claim.status = "approved"
            claim.decided_by = actor.id
            claim.decided_at = datetime.now(timezone.utc)
            claim.decided_reason = reason
            await db.commit()
            await self._audit(db, actor, "realm_claim_approved", "entity", str(claim.entity_id),
                              reason=reason or "governance approved")
        else:
            registry.claim_status = "rejected"
            claim.status = "rejected"
            claim.decided_by = actor.id
            claim.decided_at = datetime.now(timezone.utc)
            claim.decided_reason = reason
            await db.commit()
            await self._audit(db, actor, "realm_claim_rejected", "entity", str(claim.entity_id),
                              reason=reason or "governance rejected")
        return {
            "claim_id": str(claim.id),
            "entity_id": str(claim.entity_id),
            "status": claim.status,
            "decided_by": str(actor.id),
            "decided_at": claim.decided_at.isoformat() if claim.decided_at else None,
        }

    async def list_claims(self, db: AsyncSession, actor, status: str = "pending") -> List[Dict]:
        gov = get_governance_service()
        if not gov.is_reviewer(actor) and not gov.has_platform_action(actor, "manage_membership"):
            raise PermissionError("reviewer/admin permission required")
        rows = (await db.execute(
            select(RealmClaim, Entity)
            .join(Entity, Entity.id == RealmClaim.entity_id)
            .where(RealmClaim.status == status)
            .order_by(RealmClaim.created_at.desc()).limit(200)
        )).all()
        result = []
        for claim, entity in rows:
            result.append({
                "claim_id": str(claim.id),
                "entity_id": str(claim.entity_id),
                "entity_name": entity.name,
                "entity_type": entity.entity_type,
                "claimant_id": str(claim.claimant_id),
                "status": claim.status,
                "reason": claim.reason,
                "created_at": claim.created_at.isoformat() if claim.created_at else None,
            })
        return result

    async def list_mine(self, db: AsyncSession, user) -> List[Dict]:
        member_rows = (await db.execute(
            select(NodeMembership.node_id).where(
                NodeMembership.user_id == user.id,
                NodeMembership.status == "active",
            )
        )).scalars().all()
        member_ids = []
        for nid in member_rows:
            try:
                member_ids.append(uuid.UUID(str(nid)))
            except (ValueError, TypeError):
                continue
        member_registries = []
        if member_ids:
            member_registries = (await db.execute(
                select(RealmRegistry).where(RealmRegistry.entity_id.in_(member_ids))
            )).scalars().all()
        registries = {str(r.id): r for r in member_registries}.values()
        result = []
        for registry in registries:
            entity = await db.get(Entity, registry.entity_id)
            if entity:
                result.append(self._realm_card(db, registry, entity))
        result.sort(key=lambda x: x.get("name") or "")
        return result

    def _realm_card(self, db, registry: RealmRegistry, entity: Entity) -> Dict:
        return {
            "entity_id": str(entity.id),
            "entity_type": entity.entity_type,
            "realm_code": registry.realm_code,
            "realm_type": registry.realm_type,
            "name": entity.name,
            "lifecycle_state": registry.lifecycle_state,
            "claim_status": registry.claim_status,
            "owner_id": str(registry.owner_id) if registry.owner_id else None,
        }

    async def get_workspace(self, db: AsyncSession, user, entity_id: str) -> Dict:
        try:
            entity = await db.get(Entity, uuid.UUID(str(entity_id)))
        except (ValueError, TypeError):
            raise ValueError("entity_id must be a valid UUID")
        if not entity:
            raise ValueError("entity not found")
        registry = await self._registry(db, entity_id)
        controlled = await self._control(db, user, entity_id)
        if not controlled and not await self._can_read(db, user, entity_id):
            raise PermissionError("realm membership required")

        evidence_rows = (await db.execute(
            select(Evidence).where(Evidence.entity_id == entity.id).order_by(Evidence.created_at.desc())
        )).scalars().all()
        evidence = [self._evidence_dict(e) for e in evidence_rows]
        verified_claims = (await db.execute(
            select(func.count(EvidenceClaim.id)).where(
                EvidenceClaim.subject_id == entity_id,
                EvidenceClaim.truth_status == "verified",
            )
        )).scalar() or 0

        relations = (await db.execute(
            select(Relationship).where(
                (Relationship.source_id == entity.id) | (Relationship.target_id == entity.id)
            ).order_by(Relationship.created_at.desc())
        )).scalars().all()

        projects = []
        if registry:
            project_rows = (await db.execute(
                select(GeoProject).where(GeoProject.realm_id == registry.id).order_by(GeoProject.created_at.desc())
            )).scalars().all()
            projects = [self._project_card(p) for p in project_rows]

        assets = (await db.execute(
            select(RealmDataAsset).where(RealmDataAsset.entity_id == entity.id).order_by(RealmDataAsset.created_at.desc())
        )).scalars().all()
        authorizations = (await db.execute(
            select(RealmDataAuthorization).where(RealmDataAuthorization.entity_id == entity.id)
            .order_by(RealmDataAuthorization.created_at.desc())
        )).scalars().all()

        timeline = []
        for ev in evidence:
            timeline.append({"type": "evidence", "label": ev["claim"], "at": ev["created_at"], "truth_status": ev["truth_status"]})
        for asset in assets:
            timeline.append({"type": "asset", "label": asset.title, "at": asset.created_at.isoformat(), "truth_status": asset.truth_status})
        for p in projects:
            timeline.append({"type": "project", "label": p["name"], "at": p["created_at"], "truth_status": p["truth_status"]})
        timeline.sort(key=lambda x: x.get("at") or "", reverse=True)

        unknown = []
        if not evidence_rows:
            unknown.append("未导入自有数据/Evidence")
        if not verified_claims:
            unknown.append("尚无经过治理验证的 EvidenceClaim")
        if not relations:
            unknown.append("尚未建立 Realm 关系")
        if not projects:
            unknown.append("尚未创建 GEO Project")
        if not assets:
            unknown.append("尚无数据资产清单")

        return {
            "identity": {
                "id": str(entity.id),
                "name": entity.name,
                "entity_type": entity.entity_type,
                "description": entity.description,
                "geo_id": entity.geo_id,
                "is_verified": entity.is_verified,
            },
            "realm": {
                "id": str(registry.id) if registry else None,
                "realm_code": registry.realm_code if registry else None,
                "realm_type": registry.realm_type if registry else None,
                "lifecycle_state": registry.lifecycle_state if registry else "unknown",
                "claim_status": registry.claim_status if registry else "none",
                "owner_id": str(registry.owner_id) if registry and registry.owner_id else None,
            },
            "access": {
                "controlled": controlled,
                "can_import": controlled,
                "can_create_project": controlled,
                "can_verify": False,
            },
            "position": {
                "trust": {
                    "verified_evidence": sum(1 for e in evidence_rows if e.truth_status == "verified"),
                    "observed_evidence": sum(1 for e in evidence_rows if e.truth_status == "observed"),
                    "synthetic_evidence": sum(1 for e in evidence_rows if e.is_synthetic or e.truth_status == "synthetic"),
                    "verified_claims": verified_claims,
                }
            },
            "evidence": evidence,
            "relationships": [self._relationship_dict(r) for r in relations],
            "projects": projects,
            "assets": [self._asset_dict(a) for a in assets],
            "authorizations": [self._authorization_dict(a) for a in authorizations],
            "timeline": timeline,
            "unknown": unknown,
            "not_available": {
                "reputation_change": "disabled without Trust Foundation Law Mutation",
                "auto_verified": "domain owner data cannot become verified automatically",
                "ai_recommendation": "not part of V10-P0",
            },
        }

    async def add_relationship(self, db: AsyncSession, user, entity_id: str, data: Dict) -> Dict:
        if not await self._control(db, user, entity_id):
            raise PermissionError("realm owner/editor permission required")
        target_id = data.get("target_id")
        relation_type = (data.get("relation_type") or "").strip()
        if not target_id or not relation_type:
            raise ValueError("target_id and relation_type are required")
        rel = Relationship(
            source_type=data.get("source_type", "realm"),
            source_id=uuid.UUID(str(entity_id)),
            target_type=data.get("target_type", "realm"),
            target_id=uuid.UUID(str(target_id)),
            relation_type=relation_type,
            weight=float(data.get("weight", 1.0)),
            description=data.get("description"),
            metadata_={"source": "realm_owner", "realm_controlled": True},
        )
        db.add(rel)
        await db.commit()
        await db.refresh(rel)
        await self._audit(db, user, "realm_relationship_created", "relationship", str(rel.id),
                          reason=relation_type)
        return self._relationship_dict(rel)

    async def create_authorization(self, db: AsyncSession, user, entity_id: str, data: Dict) -> Dict:
        if not await self._control(db, user, entity_id):
            raise PermissionError("realm owner/editor permission required")
        use_scope = (data.get("use_scope") or "").strip()
        allowed = set(self.config.get("data_authorization", {}).get("allowed_use_scopes", []))
        if use_scope not in allowed:
            raise ValueError(f"use_scope must be one of {sorted(allowed)}")
        truth = (data.get("truth_status") or "observed").strip()
        if truth not in ("observed", "synthetic"):
            raise ValueError("realm owner authorization cannot declare verified")
        grantee_type = (data.get("grantee_type") or "").strip() or None
        if grantee_type:
            allowed_grantees = set(self.config.get("data_authorization", {}).get("grantee_types", []))
            if grantee_type not in allowed_grantees:
                raise ValueError(f"grantee_type must be one of {sorted(allowed_grantees)}")
        sensitive = (data.get("sensitive_level") or "none").strip()
        allowed_sensitive = set(self.config.get("data_authorization", {}).get("sensitive_levels", []))
        if sensitive not in allowed_sensitive:
            raise ValueError(f"sensitive_level must be one of {sorted(allowed_sensitive)}")
        code = f"AUTH-{secrets.token_urlsafe(32)}"
        valid_until = self._parse_dt(data.get("valid_until"))
        valid_from = self._parse_dt(data.get("valid_from"))
        now = datetime.now(timezone.utc)
        if use_scope == "intake_submission":
            if not valid_until:
                raise ValueError("intake_submission authorization requires valid_until")
            valid_until_utc = valid_until
            if valid_until_utc.tzinfo is None:
                valid_until_utc = valid_until_utc.replace(tzinfo=timezone.utc)
            if valid_until_utc <= now:
                raise ValueError("valid_until must be in the future")
        payload = {
            "entity_id": str(entity_id),
            "grantee_type": grantee_type,
            "grantee_id": data.get("grantee_id"),
            "provider": data.get("provider"),
            "tool_name": data.get("tool_name"),
            "use_scope": use_scope,
            "valid_from": valid_from.isoformat() if valid_from else None,
            "valid_until": valid_until.isoformat() if valid_until else None,
            "truth_status": truth,
            "allow_external_processing": bool(data.get("allow_external_processing", False)),
            "allow_derived_content": bool(data.get("allow_derived_content", False)),
            "sensitive_level": sensitive,
            "deletion_policy": data.get("deletion_policy"),
        }
        auth_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:32]
        auth = RealmDataAuthorization(
            authorization_code=code,
            entity_id=uuid.UUID(str(entity_id)),
            owner_id=user.id,
            granted_to_id=uuid.UUID(str(data["granted_to_id"])) if data.get("granted_to_id") else None,
            grantee_type=grantee_type,
            grantee_id=data.get("grantee_id"),
            provider=data.get("provider"),
            tool_name=data.get("tool_name"),
            source_name=data.get("source_name"),
            source_url=data.get("source_url"),
            source_type=data.get("source_type"),
            license=data.get("license"),
            use_scope=use_scope,
            valid_from=valid_from,
            valid_until=valid_until,
            truth_status=truth,
            may_affect_real_metrics=False,
            status="active",
            sensitive_level=sensitive,
            data_scope=data.get("data_scope"),
            allow_external_processing=bool(data.get("allow_external_processing", False)),
            allow_derived_content=bool(data.get("allow_derived_content", False)),
            retention_until=self._parse_dt(data.get("retention_until")),
            deletion_policy=data.get("deletion_policy"),
            authorization_hash=auth_hash,
            metadata_json=data.get("metadata"),
        )
        db.add(auth)
        await db.commit()
        await db.refresh(auth)
        await self._audit(db, user, "realm_authorization_created", "realm_data_authorization", str(auth.id),
                          reason=use_scope)
        return self._authorization_dict(auth, include_code=True)

    async def revoke_authorization(self, db: AsyncSession, user, entity_id: str,
                                   authorization_id: str, reason: str = None) -> Dict:
        if not await self._control(db, user, entity_id):
            raise PermissionError("realm owner/editor permission required")
        try:
            auth = await db.get(RealmDataAuthorization, uuid.UUID(str(authorization_id)))
        except (ValueError, TypeError):
            raise ValueError("authorization_id must be a valid UUID")
        if not auth or str(auth.entity_id) != str(entity_id):
            raise ValueError("authorization not found")
        if auth.status == "revoked":
            return self._authorization_dict(auth)
        auth.status = "revoked"
        auth.revoked_at = datetime.now(timezone.utc)
        auth.revoked_by = user.id
        auth.revocation_reason = reason
        await db.commit()
        await db.refresh(auth)
        await self._audit(db, user, "realm_authorization_revoked", "realm_data_authorization", str(auth.id),
                          reason=reason or "owner revoked")
        return self._authorization_dict(auth)

    async def validate_authorization(self, db: AsyncSession, authorization_id: str,
                                     entity_id: str = None, provider: str = None,
                                     tool_name: str = None, use_scope: str = None) -> Dict:
        try:
            auth = await db.get(RealmDataAuthorization, uuid.UUID(str(authorization_id)))
        except (ValueError, TypeError):
            raise ValueError("authorization_id must be a valid UUID")
        if not auth:
            raise ValueError("authorization not found")
        reasons = []
        now = datetime.now(timezone.utc)
        if auth.status != "active":
            reasons.append(f"authorization status is {auth.status}")
        if auth.valid_until and auth.valid_until < now:
            reasons.append("authorization expired")
        if entity_id and str(auth.entity_id) != str(entity_id):
            reasons.append("authorization belongs to another realm")
        if use_scope and auth.use_scope != use_scope:
            reasons.append(f"use_scope mismatch: {auth.use_scope} != {use_scope}")
        if provider and auth.grantee_type == "provider" and auth.provider and auth.provider != provider:
            reasons.append(f"provider mismatch: {auth.provider} != {provider}")
        if tool_name and auth.grantee_type == "tool" and auth.tool_name and auth.tool_name != tool_name:
            reasons.append(f"tool mismatch: {auth.tool_name} != {tool_name}")
        if provider and provider != "universe":
            if auth.use_scope != "ai_tools":
                reasons.append("external provider requires ai_tools scope")
            if not auth.allow_external_processing:
                reasons.append("external processing not authorized")
        return {
            "valid": not reasons,
            "reasons": reasons,
            "authorization": self._authorization_dict(auth),
            "authorization_hash": auth.authorization_hash,
        }

    async def create_asset(self, db: AsyncSession, user, entity_id: str, data: Dict) -> Dict:
        if not await self._control(db, user, entity_id):
            raise PermissionError("realm owner/editor permission required")
        asset_key = (data.get("asset_key") or "").strip()
        title = (data.get("title") or "").strip()
        if not asset_key or not title:
            raise ValueError("asset_key and title are required")
        existing = (await db.execute(
            select(RealmDataAsset).where(
                RealmDataAsset.entity_id == uuid.UUID(str(entity_id)),
                RealmDataAsset.asset_key == asset_key,
            )
        )).scalars().first()
        if existing:
            return self._asset_dict(existing)
        truth = (data.get("truth_status") or "observed").strip()
        if truth not in ("observed", "synthetic"):
            raise ValueError("realm asset cannot declare verified")
        may_affect = False
        authorization_id = None
        if data.get("authorization_id"):
            check = await self.validate_authorization(
                db, data["authorization_id"], entity_id=entity_id
            )
            if not check["valid"]:
                raise ValueError("; ".join(check["reasons"]))
            authorization_id = uuid.UUID(str(data["authorization_id"]))
        asset = RealmDataAsset(
            entity_id=uuid.UUID(str(entity_id)),
            project_id=uuid.UUID(str(data["project_id"])) if data.get("project_id") else None,
            authorization_id=authorization_id,
            asset_type=(data.get("asset_type") or "document").strip(),
            asset_key=asset_key,
            title=title,
            description=data.get("description"),
            owner_id=user.id,
            source_ref=data.get("source_ref"),
            truth_status=truth,
            may_affect_real_metrics=may_affect,
            metadata_json=data.get("metadata"),
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        await self._audit(db, user, "realm_asset_created", "realm_data_asset", str(asset.id),
                          reason=asset_key)
        return self._asset_dict(asset)

    async def get_tool_configs(self, db: AsyncSession, user, entity_id: str) -> Dict:
        if not await self._control(db, user, entity_id):
            raise PermissionError("realm owner/editor permission required")
        rows = (
            await db.execute(
                select(RealmDataAsset).where(
                    RealmDataAsset.entity_id == uuid.UUID(str(entity_id)),
                    RealmDataAsset.asset_type == "tool_config",
                )
            )
        ).scalars().all()
        result = {}
        for row in rows:
            key = (row.asset_key or "").replace("tool_config:", "")
            result[key] = row.metadata_json or {}
        return result

    async def save_tool_config(self, db: AsyncSession, user, entity_id: str, key: str, data: Dict) -> Dict:
        if not await self._control(db, user, entity_id):
            raise PermissionError("realm owner/editor permission required")
        key = key.strip()
        if key not in ("agent", "skill", "workflow", "mcp"):
            raise ValueError("invalid tool config key")
        asset_key = f"tool_config:{key}"
        existing = (
            await db.execute(
                select(RealmDataAsset).where(
                    RealmDataAsset.entity_id == uuid.UUID(str(entity_id)),
                    RealmDataAsset.asset_key == asset_key,
                )
            )
        ).scalars().first()
        if existing:
            existing.metadata_json = data
            existing.title = f"{key} config"
            existing.description = "四原语配置草稿"
            existing.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(existing)
            return self._asset_dict(existing)
        asset = RealmDataAsset(
            entity_id=uuid.UUID(str(entity_id)),
            asset_type="tool_config",
            asset_key=asset_key,
            title=f"{key} config",
            description="四原语配置草稿",
            owner_id=user.id,
            truth_status="observed",
            may_affect_real_metrics=False,
            metadata_json=data,
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        await self._audit(db, user, "tool_config_saved", "realm_data_asset", str(asset.id),
                          reason=key)
        return self._asset_dict(asset)

    async def create_evidence(self, db: AsyncSession, user, entity_id: str, data: Dict) -> Dict:
        if not await self._control(db, user, entity_id):
            raise PermissionError("realm owner/editor permission required")
        claim = (data.get("claim") or "").strip()
        source_url = (data.get("source_url") or "").strip()
        if not claim or not source_url:
            raise ValueError("claim and source_url are required")
        truth = (data.get("truth_status") or "observed").strip()
        if truth not in ("observed", "synthetic"):
            raise ValueError("realm owner can only submit observed or synthetic evidence")
        auth = None
        may_affect = False
        if data.get("authorization_id"):
            check = await self.validate_authorization(
                db, data["authorization_id"], entity_id=entity_id
            )
            if not check["valid"]:
                raise ValueError("; ".join(check["reasons"]))
            auth = await db.get(RealmDataAuthorization, uuid.UUID(str(data["authorization_id"])))
        license_value = data.get("license")
        if not license_value and auth is not None:
            license_value = auth.license
        ev = Evidence(
            entity_id=uuid.UUID(str(entity_id)),
            entity_type=data.get("entity_type") or "company",
            claim=claim,
            source_url=source_url,
            source_name=data.get("source_name"),
            source_description=data.get("source_description"),
            source_type=data.get("source_type"),
            truth_status=truth,
            is_synthetic=(truth == "synthetic"),
            may_affect_real_metrics=may_affect,
            confidence_level=float(data.get("confidence_level", 0.0)),
            occurred_at=self._parse_dt(data.get("occurred_at")),
            effective_at=self._parse_dt(data.get("effective_at")),
            expires_at=self._parse_dt(data.get("expires_at")),
            source_license=license_value,
            excerpt=data.get("excerpt"),
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        await self._audit(db, user, "realm_evidence_submitted", "evidence", str(ev.id),
                          reason="owner submitted data, not auto-verified")
        return self._evidence_dict(ev)

    async def boundary(self, db: AsyncSession) -> Dict:
        total = (await db.execute(select(func.count(RealmRegistry.id)))).scalar() or 0
        claimed = (await db.execute(
            select(func.count(RealmRegistry.id)).where(RealmRegistry.lifecycle_state == "claimed")
        )).scalar() or 0
        assets = (await db.execute(select(func.count(RealmDataAsset.id)))).scalar() or 0
        return {
            "realms": total,
            "claimed_realms": claimed,
            "data_assets": assets,
            "synthetic_isolated": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _evidence_dict(self, e: Evidence) -> Dict:
        return {
            "id": str(e.id),
            "entity_id": str(e.entity_id),
            "claim": e.claim,
            "source_url": e.source_url,
            "source_name": e.source_name,
            "truth_status": e.truth_status,
            "is_synthetic": e.is_synthetic,
            "may_affect_real_metrics": e.may_affect_real_metrics,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }

    def _relationship_dict(self, r: Relationship) -> Dict:
        return {
            "id": str(r.id),
            "source_id": str(r.source_id) if r.source_id else None,
            "target_id": str(r.target_id) if r.target_id else None,
            "relation_type": r.relation_type,
            "weight": r.weight,
            "description": r.description,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }

    @staticmethod
    def _mask_authorization_code(code: str) -> str:
        if not code:
            return ""
        if len(code) <= 14:
            return f"{code[:6]}••••"
        return f"{code[:14]}••••{code[-4:]}"

    def _authorization_dict(self, a: RealmDataAuthorization, include_code: bool = False) -> Dict:
        now = datetime.now(timezone.utc)
        effective = a.status
        if effective == "active" and a.valid_until and a.valid_until < now:
            effective = "expired"
        result = {
            "id": str(a.id),
            "grantee_type": a.grantee_type,
            "grantee_id": a.grantee_id,
            "provider": a.provider,
            "tool_name": a.tool_name,
            "source_name": a.source_name,
            "source_url": a.source_url,
            "source_type": a.source_type,
            "license": a.license,
            "use_scope": a.use_scope,
            "valid_from": a.valid_from.isoformat() if a.valid_from else None,
            "valid_until": a.valid_until.isoformat() if a.valid_until else None,
            "truth_status": a.truth_status,
            "may_affect_real_metrics": a.may_affect_real_metrics,
            "status": effective,
            "revoked_at": a.revoked_at.isoformat() if a.revoked_at else None,
            "revoked_by": str(a.revoked_by) if a.revoked_by else None,
            "revocation_reason": a.revocation_reason,
            "sensitive_level": a.sensitive_level,
            "data_scope": a.data_scope,
            "allow_external_processing": a.allow_external_processing,
            "allow_derived_content": a.allow_derived_content,
            "retention_until": a.retention_until.isoformat() if a.retention_until else None,
            "deletion_policy": a.deletion_policy,
            "authorization_hash": a.authorization_hash,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        result["authorization_code_masked"] = self._mask_authorization_code(a.authorization_code)
        if include_code:
            result["authorization_code"] = a.authorization_code
        return result

    def _asset_dict(self, a: RealmDataAsset) -> Dict:
        return {
            "id": str(a.id),
            "entity_id": str(a.entity_id),
            "project_id": str(a.project_id) if a.project_id else None,
            "authorization_id": str(a.authorization_id) if a.authorization_id else None,
            "asset_type": a.asset_type,
            "asset_key": a.asset_key,
            "title": a.title,
            "description": a.description,
            "source_ref": a.source_ref,
            "truth_status": a.truth_status,
            "may_affect_real_metrics": a.may_affect_real_metrics,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }

    def _project_card(self, p: GeoProject) -> Dict:
        return {
            "id": str(p.id),
            "project_code": p.project_code,
            "name": p.name,
            "status": p.status,
            "lifecycle_state": p.lifecycle_state,
            "truth_status": p.truth_status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }

    @staticmethod
    def _parse_dt(value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None


def get_realm_service() -> RealmService:
    return RealmService()
