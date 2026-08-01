"""C6.1 Continuous Learning Loop API.

Evidence-driven updates: observations -> candidate changes -> review -> apply.
Every approve/reject/apply records actor and reason.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.services.learning_loop import LearningLoopService
from app.services.governance import get_governance_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/universe", tags=["learning-loop"])


@router.post("/observations")
async def create_observation(data: dict, db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    """Submit a new observation.

    C6.2: actor comes from the authenticated user. node_owner/node_editor may
    submit user evidence and profile updates; reviewer/admin may submit
    verification changes and admin observations.
    """
    gov = get_governance_service()
    change_type = data.get("change_type", "")
    actor = str(current_user.id)
    if change_type in ("user_evidence", "profile_update"):
        ok = await gov.can_node_action(db, current_user, str(data.get("node_id", "")), "submit_evidence")
        if not ok and change_type == "profile_update":
            ok = await gov.can_node_action(db, current_user, str(data.get("node_id", "")), "create_change")
        if not ok:
            raise HTTPException(403, "node owner/editor permission required")
    elif change_type in ("evidence_verification_change", "admin_observation"):
        if not gov.has_platform_action(current_user, "evidence_verify"):
            raise HTTPException(403, "reviewer/admin permission required")
    svc = LearningLoopService()
    try:
        cc = await svc.create_observation(db, data, actor_id=actor)
    except ValueError as e:
        raise HTTPException(400, str(e))
    await gov.audit(db, current_user.id, "observation_created", "candidate_change", str(cc.id), actor_label=current_user.name)
    return svc._to_dict(cc)


@router.get("/changes")
async def list_changes(
    status: Optional[str] = Query(None),
    node_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Query candidate changes (filter by review_status and/or node)."""
    svc = LearningLoopService()
    return {"count": len(await svc.list_changes(db, status, node_id, limit)),
            "changes": await svc.list_changes(db, status, node_id, limit)}


@router.get("/changes/{change_id}")
async def get_change(change_id: str, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """View a change with evidence and impact scope."""
    svc = LearningLoopService()
    try:
        result = await svc.get_change(db, change_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return result


@router.post("/changes/{change_id}/approve")
async def approve_change(change_id: str, data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """Approve a change (reviewer/admin only). Actor comes from the session."""
    gov = get_governance_service()
    if not gov.is_reviewer(current_user):
        raise HTTPException(403, "reviewer/admin permission required")
    if not (data.get("reason") or "").strip():
        raise HTTPException(400, "reason is required for approval")
    svc = LearningLoopService()
    try:
        cc = await svc.approve(db, change_id, str(current_user.id), data.get("reason", ""))
    except ValueError as e:
        raise HTTPException(400, str(e))
    await gov.audit(db, current_user.id, "change_approved", "candidate_change", str(cc.id),
                    reason=data.get("reason"), actor_label=current_user.name)
    return svc._to_dict(cc)


@router.post("/changes/{change_id}/reject")
async def reject_change(change_id: str, data: dict, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    """Reject a change (reviewer/admin only). Actor comes from the session."""
    gov = get_governance_service()
    if not gov.is_reviewer(current_user):
        raise HTTPException(403, "reviewer/admin permission required")
    reason = (data.get("reason") or "").strip() or "no reason"
    svc = LearningLoopService()
    try:
        cc = await svc.reject(db, change_id, str(current_user.id), reason)
    except ValueError as e:
        raise HTTPException(400, str(e))
    await gov.audit(db, current_user.id, "change_rejected", "candidate_change", str(cc.id),
                    reason=reason, actor_label=current_user.name)
    return svc._to_dict(cc)


@router.post("/changes/{change_id}/apply")
async def apply_change(change_id: str, data: dict = None, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """Apply an approved change (system_admin only; system service executes)."""
    gov = get_governance_service()
    if not gov.has_platform_action(current_user, "change_apply"):
        raise HTTPException(403, "system_admin permission required")
    svc = LearningLoopService()
    try:
        cc = await svc.apply(db, change_id, str(current_user.id))
    except ValueError as e:
        raise HTTPException(400, str(e))
    await gov.audit(db, current_user.id, "change_applied", "candidate_change", str(cc.id),
                    actor_label=current_user.name)
    return svc._to_dict(cc)


@router.get("/nodes/{node_id}/learning-history")
async def learning_history(node_id: str, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    """View a node's learning history."""
    svc = LearningLoopService()
    return {"node_id": node_id, "history": await svc.get_learning_history(db, node_id)}


@router.post("/nodes/{node_id}/rebuild")
async def rebuild_node(node_id: str, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """Rebuild derived state from events and evidence (system_admin only)."""
    gov = get_governance_service()
    if not gov.has_platform_action(current_user, "node_rebuild"):
        raise HTTPException(403, "system_admin permission required")
    await gov.audit(db, current_user.id, "node_rebuild", "node", node_id, actor_label=current_user.name)
    svc = LearningLoopService()
    from app.universe.context_engine import get_context_engine
    ctx = get_context_engine().understand(node_id, "company", {})
    return {
        "node_id": node_id,
        "rebuilt": True,
        "position": ctx.current_position.get("position", {}),
        "reputation": ctx.reputation_profile.get("overview", {}),
    }
