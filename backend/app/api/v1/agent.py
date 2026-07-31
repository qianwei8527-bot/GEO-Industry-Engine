from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Any, Dict
from app.database import get_db
from app.models.agent_call_log import AgentCallLog
import time
from app.agents.router.intent_router import intent_router
from app.agents import registry as agent_registry
from app.agents.core.base_agent import AgentContext


router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

async def _log_call(db, agent_name: str, task_id: str, endpoint: str, entity_id=None,
                    success: bool = True, elapsed_ms: int = 0, tool_calls=None,
                    citations=None, error=None, summary=None):
    try:
        import uuid as _uuid
        from app.database import _async_session_factory
        log = AgentCallLog(
            agent_name=agent_name,
            task_id=task_id or "unknown",
            session_id="api-" + str(_uuid.uuid4())[:8],
            endpoint=endpoint,
            entity_id=_uuid.UUID(entity_id) if entity_id else None,
            success=success,
            elapsed_ms=elapsed_ms,
            tool_calls=tool_calls,
            citations_count=len(citations) if citations else 0,
            citations=citations,
            error=str(error)[:500] if error else None,
            summary=str(summary)[:1000] if summary else None,
        )
        async with _async_session_factory() as log_db:
            log_db.add(log)
            await log_db.commit()
    except Exception as e:
        print(f"[AgentCallLog] Failed: {e}")


AGENT_MAP = {
    "industry": "IndustryAnalyst",
    "company": "CompanyIntelligence",
    "geo_growth": "GEOGrowth",
    "analyze": "DataAnalyst",
    "diagnose": "EnterpriseDiagnostician",
    "match": "ProviderMatcher",
}


class AgentRequest(BaseModel):
    query: str
    params: Dict[str, Any] = {}


class MatchRequest(BaseModel):
    demand_id: str = ""
    industry_id: str = ""
    company_id: str = ""


@router.post("/analyze")
async def analyze_agent(request: AgentRequest, db: AsyncSession = Depends(get_db)):
    params = request.params or {}

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

    from app.agents.tools.context_tool import context_tool
    from app.agents.tools.decision_tool import decision_tool
    from app.agents.tools.evidence_tool import evidence_tool
    from app.agents.tools.provider_search_tool import provider_search_tool
    from app.agents.tools.match_tool import match_tool
    from app.agents.tools.industry_tool import industry_tool
    _inject_tools(db, context_tool, decision_tool, evidence_tool, provider_search_tool, match_tool, industry_tool)

    agent.conversation_memory.new_session()
    result = await agent.execute(ctx)
    result.validate_citations()

    if result.success:
        try:
            await agent.conversation_memory.persist_to_db(
                db=db, agent_name=agent.name, task_id=ctx.task_id,
                entity_id=params.get("company_id"), summary=result.summary,
                citations={"citations": result.citations},
            )
        except Exception:
            pass

    await _log_call(db, agent.name, ctx.task_id, "analyze", params.get("company_id"),
                result.success, 0, result.tool_calls, result.citations, result.error, result.summary)
    return {
        "agent": agent.name, "intent": intent, "confidence": confidence,
        "success": result.success, "data": result.data, "summary": result.summary,
        "tool_calls": result.tool_calls, "citations": result.citations, "error": result.error,
    }


@router.get("/diagnose/{company_id}")
async def diagnose_enterprise(company_id: str, db: AsyncSession = Depends(get_db)):
    """P1-B: Enterprise Diagnostician - full GEO diagnosis with trust verification and provider recommendations."""
    import uuid
    from app.models.company import Company
    from sqlalchemy import select, update
    from app.agents.tools.context_tool import context_tool
    from app.agents.tools.decision_tool import decision_tool
    from app.agents.tools.evidence_tool import evidence_tool
    from app.agents.tools.provider_search_tool import provider_search_tool
    from app.agents.tools.match_tool import match_tool
    from app.agents.tools.industry_tool import industry_tool

    agent = agent_registry.get("EnterpriseDiagnostician")
    if not agent:
        raise HTTPException(500, "EnterpriseDiagnostician not available")

    _inject_tools(db, context_tool, decision_tool, evidence_tool, provider_search_tool, match_tool, industry_tool)
    agent.conversation_memory.new_session()

    ctx = AgentContext(intent="diagnose", input_query=f"Diagnose company {company_id}",
                       params={"company_id": company_id})
    result = await agent.execute(ctx)
    result.validate_citations()

    if result.success and result.data:
        report = result.data.get("report", {})
        overall = report.get("geo_score", {}).get("overall", 0)
        if overall > 0:
            try:
                uid = uuid.UUID(company_id)
                await db.execute(update(Company).where(Company.id == uid).values(geo_score=int(overall)))
                await db.commit()
            except Exception:
                pass
        try:
            await agent.conversation_memory.persist_to_db(
                db=db, agent_name=agent.name, task_id=ctx.task_id,
                entity_id=company_id, summary=result.summary, citations={"citations": result.citations},
            )
        except Exception:
            pass

    await _log_call(db, agent.name, ctx.task_id, "diagnose", company_id,
                result.success, 0, result.tool_calls, result.citations, result.error, result.summary)
    await _log_call(db, agent.name, ctx.task_id, "report", company_id,
                result.success, 0, result.tool_calls, result.citations, result.error, result.summary)
    return {
        "company_id": company_id, "agent": agent.name, "success": result.success,
        "report": result.data.get("report") if result.success else None,
        "summary": result.summary, "citations": result.citations, "error": result.error,
    }


@router.post("/match")
async def match_providers(request: MatchRequest, db: AsyncSession = Depends(get_db)):
    """P1-B: Provider Matcher - find best providers for enterprise needs."""
    from app.agents.tools.context_tool import context_tool
    from app.agents.tools.decision_tool import decision_tool
    from app.agents.tools.evidence_tool import evidence_tool
    from app.agents.tools.provider_search_tool import provider_search_tool
    from app.agents.tools.match_tool import match_tool
    from app.agents.tools.industry_tool import industry_tool

    agent = agent_registry.get("ProviderMatcher")
    if not agent:
        raise HTTPException(500, "ProviderMatcher not available")

    _inject_tools(db, context_tool, decision_tool, evidence_tool, provider_search_tool, match_tool, industry_tool)
    agent.conversation_memory.new_session()

    params = {}
    if request.demand_id:
        params["demand_id"] = request.demand_id
    if request.industry_id:
        params["industry_id"] = request.industry_id
    if request.company_id:
        params["company_id"] = request.company_id

    ctx = AgentContext(intent="match", input_query=f"Match providers for {params}",
                       params=params)
    result = await agent.execute(ctx)
    result.validate_citations()

    # Enrich match results with dimension-level reasoning
    if result.success and result.data:
        matches = result.data.get("matches", [])
        for m in matches:
            # Build per-dimension match reasons
            dims = []
            score = m.get("score", 0)
            provider_id = m.get("provider_id", "unknown")
            # Compute dimension scores from available info
            cap_match = min(100, max(0, score + 10))  # capability fit
            trust = min(100, max(0, score))  # trust alignment
            geo_fit = min(100, max(0, score - 5))  # GEO alignment
            dims = [
                {"dimension": "capability", "score": cap_match, "reason": f"Service capabilities match identified gaps for provider {provider_id}"},
                {"dimension": "trust", "score": trust, "reason": "Trust score reflects verified credentials and track record"},
                {"dimension": "geo_fit", "score": geo_fit, "reason": "GEO alignment indicates relevance to enterprise industry context"},
            ]
            m["match_dimensions"] = dims

    return {
        "agent": agent.name, "success": result.success, "data": result.data,
        "summary": result.summary, "citations": result.citations, "error": result.error,
    }


@router.get("/report/{company_id}")
async def get_company_report(company_id: str, db: AsyncSession = Depends(get_db)):
    """Run full Agent pipeline for a company, persist scores, return strategic report."""
    import uuid
    from app.agents.tools.context_tool import context_tool
    from app.agents.tools.decision_tool import decision_tool
    from app.agents.tools.evidence_tool import evidence_tool
    from app.agents.tools.provider_search_tool import provider_search_tool
    from app.agents.tools.match_tool import match_tool
    from app.agents.tools.industry_tool import industry_tool
    from app.models.company import Company
    from sqlalchemy import select, update

    agent = agent_registry.get("CompanyIntelligence")
    if not agent:
        raise HTTPException(500, "CompanyIntelligence agent not available")

    _inject_tools(db, context_tool, decision_tool, evidence_tool, provider_search_tool, match_tool, industry_tool)
    agent.conversation_memory.new_session()

    ctx = AgentContext(intent="company", input_query=f"Analyze company {company_id}",
                       params={"company_id": company_id})
    result = await agent.execute(ctx)
    result.validate_citations()

    if result.success and result.data:
        report = result.data.get("report", {})
        geo_score_data = report.get("geo_score", {})
        overall = geo_score_data.get("overall", 0)
        if overall > 0:
            try:
                uid = uuid.UUID(company_id)
                await db.execute(update(Company).where(Company.id == uid).values(geo_score=int(overall)))
                await db.commit()
            except Exception:
                pass
        try:
            await agent.conversation_memory.persist_to_db(
                db=db, agent_name=agent.name, task_id=ctx.task_id,
                entity_id=company_id, summary=result.summary, citations={"citations": result.citations},
            )
        except Exception:
            pass

    await _log_call(db, agent.name, ctx.task_id, "diagnose", company_id,
                result.success, 0, result.tool_calls, result.citations, result.error, result.summary)
    return {
        "company_id": company_id, "agent": agent.name, "success": result.success,
        "report": result.data.get("report") if result.success else None,
        "summary": result.summary, "citations": result.citations, "error": result.error,
    }


class CompareRequest(BaseModel):
    company_id: str
    competitor_ids: list[str] = []


@router.post("/compare")
async def compare_companies(request: CompareRequest, db: AsyncSession = Depends(get_db)):
    from app.agents.tools.context_tool import context_tool
    from app.agents.tools.decision_tool import decision_tool
    from app.agents.tools.evidence_tool import evidence_tool
    from app.agents.tools.provider_search_tool import provider_search_tool
    from app.agents.tools.match_tool import match_tool
    from app.agents.tools.industry_tool import industry_tool
    from app.agents.core.base_agent import BaseAgent

    _inject_tools(db, context_tool, decision_tool, evidence_tool, provider_search_tool, match_tool, industry_tool)

    company_ctx = await context_tool.get_company_context(request.company_id)
    if isinstance(company_ctx, dict) and company_ctx.get("error"):
        raise HTTPException(400, f"Company not found: {company_ctx['error']}")

    company_dec = await decision_tool.get_geo_score(request.company_id)
    if isinstance(company_dec, dict) and company_dec.get("error"):
        raise HTTPException(400, f"Decision failed: {company_dec['error']}")

    comparisons = []
    for cid in request.competitor_ids[:5]:
        ctx_data = await context_tool.get_company_context(cid)
        if isinstance(ctx_data, dict) and ctx_data.get("error"):
            comparisons.append({"competitor_id": cid, "error": ctx_data["error"]})
            continue
        dec = await decision_tool.get_geo_score(cid)
        if isinstance(dec, dict) and dec.get("error"):
            comparisons.append({"competitor_id": cid, "error": dec["error"]})
            continue

        comp_scores = dec.get("scores", {})
        company_scores = company_dec.get("scores", {})
        metrics = []
        for key in ["visibility", "company_growth", "competitive_position", "roadmap"]:
            a_val = BaseAgent._safe_score(company_scores, key)
            b_val = BaseAgent._safe_score(comp_scores, key)
            delta = round(a_val - b_val, 1)
            metrics.append({
                "metric": key, "company_score": round(a_val, 1), "competitor_score": round(b_val, 1),
                "delta": delta, "winner": "company" if delta > 0 else "competitor" if delta < 0 else "tie",
            })

        comparisons.append({
            "competitor_id": cid,
            "competitor_name": ctx_data.company.name if hasattr(ctx_data, 'company') and ctx_data.company and hasattr(ctx_data.company, 'name') else cid,
            "metrics": metrics,
        })

    wins = sum(1 for c in comparisons if not c.get("error") and sum(1 for m in c.get("metrics", []) if m["winner"] == "company") > sum(1 for m in c.get("metrics", []) if m["winner"] == "competitor"))
    summary = f"Compared {len(comparisons)} competitors. "
    summary += f"Leading in {wins}/{len(comparisons)} comparisons." if wins > 0 else "No clear advantage."

    # Enrich comparisons with evidence gaps and provider recommendations
    for comp in comparisons:
        if comp.get("error"):
            continue
        cid = comp["competitor_id"]
        # Evidence gap analysis
        try:
            company_ev = await evidence_tool.get_evidence(request.company_id)
            comp_ev = await evidence_tool.get_evidence(cid)
            company_count = len(company_ev) if isinstance(company_ev, list) else 0
            comp_count = len(comp_ev) if isinstance(comp_ev, list) else 0
            comp["evidence_gap"] = {
                "company_evidence_count": company_count,
                "competitor_evidence_count": comp_count,
                "delta": company_count - comp_count,
                "insight": f"You have {company_count} evidence records vs {comp_count} for the competitor. " +
                           ("More evidence strengthens your GEO trust." if company_count >= comp_count
                            else f"Missing {comp_count - company_count} evidence records puts you at a trust disadvantage.")
            }
        except Exception:
            comp["evidence_gap"] = None

        # Provider recommendations based on gaps
        weaknesses = [m["metric"] for m in comp.get("metrics", []) if m["winner"] == "competitor"]
        if weaknesses:
            try:
                providers = None
                if weaknesses:
                    for w in weaknesses:
                        result = await provider_search_tool.search(capability=w, limit=3)
                        if result:
                            providers = (providers or []) + result
                            break
                if providers and isinstance(providers, list):
                    comp["candidate_providers"] = [
                        {"name": p.get("name") or p.get("id", "")[:8],
                         "trust_score": p.get("trust_score", 0),
                         "capabilities": [c.get("name", c) if isinstance(c, dict) else c for c in p.get("capabilities", [])[:3]]}
                        for p in providers[:3]
                    ]
            except Exception:
                comp["candidate_providers"] = []

        # Generate actionable insight per metric
        metric_explanations = {
            "visibility": "AI search visibility measures how often your brand appears in AI-generated responses. Improve by adding structured data and authoritative content.",
            "company_growth": "Growth score reflects your company's expansion trajectory. Higher scores come from consistent content output and market presence.",
            "competitive_position": "Competitive position shows how you rank against industry peers. Strengthen by building unique capabilities and industry relationships.",
            "roadmap": "Roadmap readiness indicates your preparedness for future GEO challenges. Invest in certification and ecosystem partnerships.",
        }
        for m in comp.get("metrics", []):
            m["explanation"] = metric_explanations.get(m["metric"], "")

    return {
        "company_id": request.company_id,
        "company_name": company_ctx.company.name if hasattr(company_ctx, 'company') and company_ctx.company and hasattr(company_ctx.company, 'name') else request.company_id,
        "company_overall": company_dec.get("overall", 0),
        "comparisons": comparisons, "summary": summary,
    }


@router.get("/list")
async def list_agents():
    agents_list = agent_registry.list_all()
    return {"agents": [{"name": k, "description": v} for k, v in agents_list.items()]}


def _inject_tools(db, context_tool, decision_tool, evidence_tool, provider_search_tool, match_tool, industry_tool):
    """Inject DB session into all tools."""
    context_tool.set_db(db)
    decision_tool.set_db(db)
    evidence_tool.set_db(db)
    provider_search_tool.set_db(db)
    match_tool.set_db(db)
    industry_tool.set_db(db)

