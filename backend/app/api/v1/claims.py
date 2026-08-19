"""C8.1-R EvidenceClaim API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.evidence_claim import get_evidence_claim_service

router = APIRouter(prefix="/api/v1/universe/claims", tags=["claims"])


@router.post("")
async def create_claim(data: dict, db: AsyncSession = Depends(get_db)):
    svc = get_evidence_claim_service()
    try:
        return await svc.create_claim(
            db, data.get("evidence_id", ""), data.get("subject_type", ""),
            data.get("subject_id", ""), data.get("predicate_code", ""),
            data.get("object_type", "concept"), data.get("object_code", ""),
            data.get("object_value"), data.get("claim_text"),
            data.get("source_locator"), data.get("extraction_method", "structured"),
            data.get("valid_from"), data.get("valid_until"),
            data.get("metadata"),
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{claim_id}/verify")
async def verify_claim(claim_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    svc = get_evidence_claim_service()
    try:
        return await svc.verify_claim(db, claim_id, data.get("verifier_id", ""),
                                      data.get("verification_method", "structured_review"),
                                      data.get("verification_result", "approved"))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("")
async def list_claims(evidence_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    return {"claims": await get_evidence_claim_service().list_for_evidence(db, evidence_id)}


@router.get("/review")
async def review_claims(status: str = Query("observed"), limit: int = Query(100, ge=1, le=200),
                        db: AsyncSession = Depends(get_db)):
    return {"claims": await get_evidence_claim_service().list_review(db, status, limit)}
