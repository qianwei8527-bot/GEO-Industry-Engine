from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Any, Dict
from app.database import get_db
from app.agents.router.intent_router import intent_router
from app.agents import registry as agent_registry


router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

AGENT_MAP = {
    "industry": "IndustryAnalyst",
    "company": "CompanyIntelligence",
    "geo_growth": "GEOGrowth",
    "analyze": "DataAnalyst",
}


class AgentRequest(BaseModel):
    query: str
    params: Dict[str, Any] = {}


@router.post("/analyze")
async def analyze_agent(request: AgentRequest, db: AsyncSession = Depends(get_db)):
    params = request.params or {}
    
    # Priority: params-driven routing > keyword routing
    if "company_id" in params:
        intent, confidence = "company", 1.0
    elif "industry_id" in params:
        intent, confidence = "industry", 1.0
    else:
        intent, confidence = intent_router.route(request.query)
    
    agent_name = AGENT_MAP.get(intent)
    if not agent_name:
        raise HTTPException(status_code=404, detail=f"No agent available for: {request.query}")

    agent = agent_registry.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found in registry")

    ctx = intent_router.build_context(request.query, request.params)
    if "company_id" not in params and "industry_id" not in params:
        params["query"] = request.query
    ctx.params = params

    # Inject db session into tools
    from app.agents.tools.context_tool import context_tool
    from app.agents.tools.decision_tool import decision_tool
    context_tool.set_db(db)
    decision_tool.set_db(db)

    result = await agent.execute(ctx)
    return {
        "agent": agent.name,
        "intent": intent,
        "confidence": confidence,
        "success": result.success,
        "data": result.data,
        "summary": result.summary,
        "tool_calls": result.tool_calls,
        "error": result.error,
    }


@router.get("/list")
async def list_agents():
    agents_list = agent_registry.list_all()
    return {"agents": [{"name": k, "description": v} for k, v in agents_list.items()]}
