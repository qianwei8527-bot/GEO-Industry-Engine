"""Knowledge Recognition API - tracks what Universe is learning."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.knowledge_candidate import KnowledgeCandidate

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


class AssessRequest(BaseModel):
    target_state: str
    recognized_by: Optional[str] = "admin"
    rejection_reason: Optional[str] = None


def compute_emergence_score(occurrence: int, persistence_days: int, source_diversity: int, impact: float) -> float:
    o = min(1.0, occurrence / 20.0)
    p = min(1.0, persistence_days / 90.0)
    d = min(1.0, source_diversity / 8.0)
    i = impact or 0.1
    return round(0.25 * o + 0.30 * p + 0.20 * d + 0.25 * i, 4)


@router.get("/candidates")
async def list_candidates(
    recognition_state: Optional[str] = Query(None),
    concept_type: Optional[str] = Query(None),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
):
    q = select(KnowledgeCandidate)
    if recognition_state:
        q = q.where(KnowledgeCandidate.recognition_state == recognition_state)
    if concept_type:
        q = q.where(KnowledgeCandidate.concept_type == concept_type)
    q = q.order_by(KnowledgeCandidate.emergence_score.desc()).limit(limit)
    rows = (await db.execute(q)).scalars().all()
    return {
        "count": len(rows),
        "candidates": [
            {
                "id": str(r.id), "concept_name": r.concept_name,
                "concept_type": r.concept_type,
                "recognition_state": r.recognition_state,
                "confidence": r.confidence,
                "occurrence_count": r.occurrence_count,
                "persistence_days": r.persistence_days,
                "source_diversity": r.source_diversity,
                "impact_score": r.impact_score,
                "emergence_score": r.emergence_score,
                "first_observed_at": str(r.first_observed_at) if r.first_observed_at else None,
                "suggested_node_fields": r.suggested_node_fields,
            }
            for r in rows
        ],
    }


@router.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    r = (await db.execute(
        select(KnowledgeCandidate).where(KnowledgeCandidate.id == candidate_id)
    )).scalars().first()
    if not r:
        raise HTTPException(404, "Knowledge candidate not found")
    return {
        "id": str(r.id), "concept_name": r.concept_name,
        "concept_type": r.concept_type,
        "recognition_state": r.recognition_state,
        "confidence": r.confidence,
        "occurrence_count": r.occurrence_count,
        "persistence_days": r.persistence_days,
        "source_diversity": r.source_diversity,
        "impact_score": r.impact_score,
        "emergence_score": r.emergence_score,
        "first_observed_at": str(r.first_observed_at) if r.first_observed_at else None,
        "last_observed_at": str(r.last_observed_at) if r.last_observed_at else None,
        "recognized_at": str(r.recognized_at) if r.recognized_at else None,
        "recognized_by": r.recognized_by,
        "suggested_node_fields": r.suggested_node_fields,
        "suggested_rules": r.suggested_rules,
        "candidate_change_ids": r.candidate_change_ids,
    }


@router.post("/candidates/{candidate_id}/assess")
async def assess_candidate(candidate_id: str, req: AssessRequest, db: AsyncSession = Depends(get_db)):
    r = (await db.execute(
        select(KnowledgeCandidate).where(KnowledgeCandidate.id == candidate_id)
    )).scalars().first()
    if not r:
        raise HTTPException(404, "Knowledge candidate not found")

    valid = ["observed", "emerging", "recognized", "adopted", "rejected"]
    if req.target_state not in valid:
        raise HTTPException(422, f"Invalid state. Must be: {valid}")

    r.recognition_state = req.target_state
    r.recognized_by = req.recognized_by
    r.updated_at = datetime.now(timezone.utc)

    if req.target_state in ("recognized", "adopted"):
        r.recognized_at = datetime.now(timezone.utc)
    if req.target_state == "rejected":
        r.rejection_reason = req.rejection_reason

    await db.commit()
    return {
        "id": str(r.id), "concept_name": r.concept_name,
        "recognition_state": r.recognition_state,
        "recognized_by": r.recognized_by,
    }


@router.get("/stats")
async def knowledge_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(KnowledgeCandidate.id)))).scalar()
    by_state = {}
    for state in ["observed", "emerging", "recognized", "adopted"]:
        n = (await db.execute(
            select(func.count(KnowledgeCandidate.id)).where(
                KnowledgeCandidate.recognition_state == state
            )
        )).scalar()
        by_state[state] = n
    return {
        "total_candidates": total,
        "by_state": by_state,
        "learning": by_state["observed"] + by_state["emerging"],
        "learned": by_state["recognized"] + by_state["adopted"],
    }