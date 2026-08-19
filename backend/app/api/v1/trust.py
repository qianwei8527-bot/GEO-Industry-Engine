"""C6.11 Trust Foundation API.

Verification is a governed action:
  - reviewer/admin can verify evidence
  - system_admin can trigger Law Mutation
  - boundary counts are read-only
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.governance import get_governance_service
from app.services.trust_foundation import get_trust_foundation_service

router = APIRouter(prefix="/api/v1/universe/trust", tags=["trust"])


@router.post("/evidence/{evidence_id}/verify")
async def verify_evidence(evidence_id: str, data: dict = None,
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """Mark an evidence row as verified (reviewer/admin only)."""
    gov = get_governance_service()
    if not gov.is_reviewer(current_user):
        raise HTTPException(403, "reviewer/admin permission required")
    data = data or {}
    svc = get_trust_foundation_service()
    try:
        ev = await svc.verify_evidence(
            db, evidence_id, str(current_user.id),
            method=data.get("verification_method") or "governance_review",
            result=data.get("verification_result") or "approved",
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    await gov.audit(db, current_user.id, "evidence_verified", "evidence", str(ev.id),
                    reason=f"{ev.verification_method}:{ev.verification_result}",
                    actor_label=current_user.name)
    return {
        "id": str(ev.id),
        "verified": ev.verified,
        "truth_status": ev.truth_status,
        "verified_by": str(ev.verified_by),
        "verified_at": ev.verified_at.isoformat() if ev.verified_at else None,
        "verification_method": ev.verification_method,
        "verification_result": ev.verification_result,
    }


@router.post("/nodes/{node_id}/law-mutation")
async def trigger_law_mutation(node_id: str, db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """Trigger a verified Law Mutation (system_admin only)."""
    gov = get_governance_service()
    if not gov.has_platform_action(current_user, "change_apply"):
        raise HTTPException(403, "system_admin permission required")
    svc = get_trust_foundation_service()
    try:
        result = await svc.trigger_law_mutation(db, node_id, str(current_user.id))
    except ValueError as e:
        raise HTTPException(400, str(e))
    await gov.audit(db, current_user.id, "law_mutation_triggered", "node", node_id,
                    reason="verified trust foundation", actor_label=current_user.name)
    return result


@router.get("/boundary/{node_id}")
async def trust_boundary(node_id: str, db: AsyncSession = Depends(get_db)):
    """Trust Boundary counts for one node."""
    return await get_trust_foundation_service().boundary(db, node_id)
