from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.context.engine import ContextEngine
from app.context.schemas.context_schema import (
    CompanyContext, IndustryContext, CapabilityContext,
    ContextQueryRequest, ContextQueryResponse,
)

router = APIRouter(prefix="/api/v1/context", tags=["context"])


@router.get("/company/{company_id}", response_model=CompanyContext)
async def get_company_context(company_id: str, db: AsyncSession = Depends(get_db)):
    engine = ContextEngine(db)
    return await engine.get_company_context(company_id)


@router.get("/industry/{industry_id}", response_model=IndustryContext)
async def get_industry_context(industry_id: str, db: AsyncSession = Depends(get_db)):
    engine = ContextEngine(db)
    return await engine.get_industry_context(industry_id)


@router.get("/capability/{capability_id}", response_model=CapabilityContext)
async def get_capability_context(capability_id: str, db: AsyncSession = Depends(get_db)):
    engine = ContextEngine(db)
    return await engine.get_capability_context(capability_id)


@router.post("/query", response_model=ContextQueryResponse)
async def query_context(request: ContextQueryRequest, db: AsyncSession = Depends(get_db)):
    engine = ContextEngine(db)
    return await engine.query(request.query, request.limit, request.entity_type)
