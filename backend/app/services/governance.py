"""GovernanceService — C6.2 server-side authorization and audit.

Client never declares actor/role. All actor ids come from the authenticated
user (deps.get_current_user). Node roles come from NodeMembership.
"""
import uuid, os as _os, yaml
from datetime import datetime, timezone
from typing import Dict, List, Optional
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.governance import NodeMembership, AuditLog
from app.models.user import User

print("Phase C6.2: GovernanceService loaded")


def _load_access_config() -> Dict:
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                      'config', 'universe', 'access_control.yaml')
    if _os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


class GovernanceService:
    def __init__(self):
        self.config = _load_access_config()

    # ── Role checks ──

    def is_system_admin(self, user: User) -> bool:
        return user.role == "admin" or (user.role and user.role.value == "admin")

    def is_reviewer(self, user: User) -> bool:
        if self.is_system_admin(user):
            return True
        return bool(user.role) and getattr(user.role, "value", user.role) == "reviewer"

    def has_platform_action(self, user: User, action: str) -> bool:
        allowed = self.config.get("platform_permissions", {}).get(action, [])
        if self.is_system_admin(user):
            return True
        role = getattr(user.role, "value", user.role) if user.role else ""
        return role in allowed

    # ── Node membership ──

    async def get_membership(self, db: AsyncSession, user_id, node_id: str) -> Optional[NodeMembership]:
        return (await db.execute(
            select(NodeMembership).where(
                NodeMembership.user_id == user_id,
                NodeMembership.node_id == node_id,
                NodeMembership.status == "active",
            )
        )).scalars().first()

    async def get_node_roles(self, db: AsyncSession, user_id, node_id: str) -> List[str]:
        rows = (await db.execute(
            select(NodeMembership).where(
                NodeMembership.user_id == user_id,
                NodeMembership.node_id == node_id,
                NodeMembership.status == "active",
            )
        )).scalars().all()
        return [r.role for r in rows]

    async def add_membership(self, db: AsyncSession, user_id, node_id: str, role: str,
                             node_type: str = "company", created_by=None, accepted: bool = True) -> NodeMembership:
        existing = await self.get_membership(db, user_id, node_id)
        if existing:
            if existing.role == role:
                return existing
            existing.role = role
            await db.commit()
            await db.refresh(existing)
            return existing
        m = NodeMembership(
            user_id=uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id,
            node_id=node_id, node_type=node_type, role=role,
            created_by=created_by, accepted_at=datetime.utcnow() if accepted else None,
        )
        db.add(m)
        await db.commit()
        await db.refresh(m)
        return m

    async def revoke_membership(self, db, user_id, node_id: str, actor_id) -> bool:
        m = await self.get_membership(db, user_id, node_id)
        if not m:
            return False
        # Owner cannot be removed if they are the last owner
        if m.role == "node_owner":
            owners = (await db.execute(
                select(NodeMembership).where(
                    NodeMembership.node_id == node_id,
                    NodeMembership.role == "node_owner",
                    NodeMembership.status == "active",
                )
            )).scalars().all()
            if len(owners) <= 1:
                raise ValueError("cannot revoke the last node_owner")
        m.status = "revoked"
        m.revoked_at = datetime.utcnow()
        await db.commit()
        await self.audit(db, actor_id, "membership_revoked", "node_membership", str(m.id), reason=f"revoked {role}")
        return True

    # ── Node action permission ──

    async def can_node_action(self, db, user: User, node_id: str, action: str) -> bool:
        """Check platform + node role for a node-scoped action."""
        roles = await self.get_node_roles(db, user.id, node_id)
        role_cfg = {r['id']: r for r in self.config.get('node_roles', [])}
        action_map = {
            "submit_evidence": "can_submit_evidence",
            "create_change": "can_create_change",
            "verify_evidence": "can_verify_evidence",
            "manage_members": "can_manage_members",
        }
        cfg_key = action_map.get(action)
        if not cfg_key:
            return False
        for r in roles:
            cfg = role_cfg.get(r)
            if cfg and cfg.get(cfg_key):
                return True
        return False

    # ── Four-eyes ──

    async def four_eyes_ok(self, db, submitter_id, verifier_id, impact: str = "high") -> bool:
        if not self.config.get("four_eyes", {}).get("enabled", True):
            return True
        if impact == "high" and self.config.get("four_eyes", {}).get("high_impact_requires_different_users", True):
            return str(submitter_id) != str(verifier_id)
        return True

    # ── Audit ──

    async def audit(self, db, actor_id, action: str, target_type: str = None, target_id: str = None,
                    result: str = "ok", reason: str = None, request_id: str = None,
                    actor_label: str = None, metadata: Dict = None) -> AuditLog:
        log = AuditLog(
            actor_id=uuid.UUID(str(actor_id)) if actor_id else None,
            actor_label=actor_label,
            action=action, target_type=target_type, target_id=target_id,
            result=result, reason=reason, request_id=request_id,
            metadata_json=metadata,
        )
        db.add(log)
        await db.commit()
        return log


@lru_cache()
def get_governance_service():
    return GovernanceService()
