from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.decision.engine import DecisionEngine
from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    query: str
    limit: int = 10
    entity_type: Optional[str] = None


router = APIRouter(prefix="/api/v1/decision", tags=["decision"])


@router.get("/company/{company_id}")
async def analyze_company(company_id: str, db: AsyncSession = Depends(get_db)):
    engine = DecisionEngine(db)
    return await engine.analyze_company(company_id)


@router.get("/industry/{industry_id}")
async def analyze_industry(industry_id: str, db: AsyncSession = Depends(get_db)):
    engine = DecisionEngine(db)
    return await engine.analyze_industry(industry_id)


@router.post("/analyze")
async def analyze(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    engine = DecisionEngine(db)
    return await engine.analyze(request.query, request.limit)
