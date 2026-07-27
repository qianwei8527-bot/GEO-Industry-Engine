from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models.industry import Industry
from app.schemas.industry import IndustryCreate, IndustryResponse

router = APIRouter(prefix="/api/v1/industries", tags=["industries"])

@router.post("/", response_model=IndustryResponse, status_code=201)
async def create_industry(data: IndustryCreate, db: AsyncSession = Depends(get_db)):
    industry = Industry(**data.model_dump())
    db.add(industry)
    await db.commit()
    await db.refresh(industry)
    return IndustryResponse.model_validate(industry)

@router.get("/", response_model=List[IndustryResponse])
async def list_industries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Industry).order_by(Industry.sort_order).offset(skip).limit(limit))
    return [IndustryResponse.model_validate(i) for i in result.scalars().all()]

@router.get("/{industry_id}", response_model=IndustryResponse)
async def get_industry(industry_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Industry).where(Industry.id == industry_id))
    industry = result.scalar_one_or_none()
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    return IndustryResponse.model_validate(industry)
