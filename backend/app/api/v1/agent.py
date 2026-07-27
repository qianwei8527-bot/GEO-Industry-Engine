from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Any, Dict
from app.database import get_db
from agents.workflow.intent_router import IntentRouter
from agents.agents.industry_agent import IndustryAgent
from agents.agents.company_agent import CompanyAgent
from agents.agents.geo_growth_agent import GEOGrowthAgent
from agents.agents.analyst_agent import AnalystAgent


router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

AGENT_MAP = {
    "industry_agent": IndustryAgent,
    "company_agent": CompanyAgent,
    "geo_growth_agent": GEOGrowthAgent,
    "analyst_agent": AnalystAgent,
}


class AgentRequest(BaseModel):
    query: str
    params: Dict[str, Any] = {}


@router.post("/analyze")
async def analyze_agent(request: AgentRequest, db: AsyncSession = Depends(get_db)):
    agent_name = IntentRouter.route(request.query)
    cls = AGENT_MAP.get(agent_name)
    if not cls:
        raise HTTPException(status_code=404, detail=f"No agent available for: {request.query}")
    agent = cls(db)
    params = request.params or {}
    if "company_id" not in params and "industry_id" not in params:
        params["query"] = request.query
    return await agent.execute(params)


@router.get("/list")
async def list_agents():
    return {"agents": [{"name": k, "description": v.agent_description} for k, v in AGENT_MAP.items()]}
