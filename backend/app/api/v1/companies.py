from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from app.database import get_db
from app.models.company import Company
from app.models.capability import Capability
from app.schemas.company import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])

@router.post("/", response_model=CompanyResponse, status_code=201)
async def create_company(data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    company = Company(
        name=data.name,
        description=data.description,
        website=data.website,
        company_size=data.company_size,
        industry_id=data.industry_id,
        contact_email=data.contact_email,
        entity_type="company",
        geo_id=f"GEO-COMP-{uuid.uuid4().hex[:8].upper()}"
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return CompanyResponse.model_validate(company)

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    industry_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Company).offset(skip).limit(limit)
    if industry_id:
        stmt = stmt.where(Company.industry_id == industry_id)
    result = await db.execute(stmt)
    return [CompanyResponse.model_validate(c) for c in result.scalars().all()]

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.model_validate(company)
