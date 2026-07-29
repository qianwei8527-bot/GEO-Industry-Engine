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


@router.get("/company/{company_id}/assessment")
async def assess_company(company_id: str, db: AsyncSession = Depends(get_db)):
    engine = DecisionEngine(db)
    return await engine.assess_company(company_id)


@router.get("/industry/{industry_id}")
async def analyze_industry(industry_id: str, db: AsyncSession = Depends(get_db)):
    engine = DecisionEngine(db)
    return await engine.analyze_industry(industry_id)


@router.post("/analyze")
async def analyze(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    engine = DecisionEngine(db)
    return await engine.analyze(request.query, request.limit)

@router.get("/config/{config_name}")
async def get_config(config_name: str):
    from app.decision.scoring.weights import WeightsLoader
    from pathlib import Path
    import os
    weights = WeightsLoader.load(config_name)
    config_path = os.path.join("config", "scoring", f"{config_name}.yaml")
    raw = ""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            raw = f.read()
    return {
        "config_name": config_name,
        "weights": weights,
        "raw_yaml": raw,
        "editable": True,
    }