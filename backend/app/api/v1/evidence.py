from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate, EvidenceResponse

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])

@router.post("/", response_model=EvidenceResponse, status_code=201)
async def create_evidence(data: EvidenceCreate, db: AsyncSession = Depends(get_db)):
    ev = Evidence(**data.model_dump())
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return EvidenceResponse.model_validate(ev)

@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    target_id: str = Query(None),
    confidence_level: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Evidence).offset(skip).limit(limit)
    if target_id:
        stmt = stmt.where(Evidence.target_id == target_id)
    if confidence_level is not None:
        stmt = stmt.where(Evidence.confidence_level >= confidence_level)
    result = await db.execute(stmt)
    return [EvidenceResponse.model_validate(e) for e in result.scalars().all()]

@router.get("/{ev_id}", response_model=EvidenceResponse)
async def get_evidence(ev_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.id == ev_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return EvidenceResponse.model_validate(ev)
