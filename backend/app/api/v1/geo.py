"""C6.4 GEO Visibility API — AI answer observation.
Answers are observations; they never modify Reputation or facts.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.models.geo_visibility import QuestionSet, AIObservationRun, AIAnswerArtifact, VisibilityResult
from app.services.geo_visibility import GEOVisibilityService
from app.services.governance import get_governance_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/geo", tags=["geo-visibility"])


@router.get("/question-sets")
async def list_question_sets(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (await db.execute(select(QuestionSet).where(QuestionSet.enabled == True).limit(100))).scalars().all()
    return {"count": len(rows), "question_sets": [
        {"id": str(q.id), "set_key": q.set_key, "category": q.category, "question_text": q.question_text,
         "version": q.version, "target_entities": q.target_entities, "competitor_entities": q.competitor_entities}
        for q in rows]}


@router.post("/question-sets")
async def create_question_set(data: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a question set (admin/global template only)."""
    gov = get_governance_service()
    if not gov.is_system_admin(current_user):
        raise HTTPException(403, "system_admin permission required")
    q = QuestionSet(set_key=data.get("set_key"), category=data.get("category", "专业解释"),
                    question_text=data.get("question_text", ""), version=data.get("version", 1),
                    target_entities=data.get("target_entities"), competitor_entities=data.get("competitor_entities"),
                    industry_id=data.get("industry_id"))
    db.add(q); await db.commit(); await db.refresh(q)
    return {"id": str(q.id), "set_key": q.set_key}


@router.get("/observation-runs")
async def list_runs(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
                    limit: int = Query(30, ge=1, le=100)):
    rows = (await db.execute(select(AIObservationRun).order_by(AIObservationRun.started_at.desc()).limit(limit))).scalars().all()
    return {"count": len(rows), "runs": [
        {"id": str(r.id), "provider": r.provider, "model": r.model, "status": r.status,
         "latency_ms": r.latency_ms, "estimated_cost": r.estimated_cost, "error": r.error,
         "started_at": r.started_at.isoformat() if r.started_at else None}
        for r in rows]}


@router.post("/observation-runs")
async def create_run(data: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a run (owner/editor may run their own node; reviewers/admin any)."""
    node_id = data.get("node_id", "")
    gov = get_governance_service()
    roles = await gov.get_node_roles(db, current_user.id, node_id) if node_id else []
    if not roles and not (gov.is_system_admin(current_user) or gov.is_reviewer(current_user)):
        raise HTTPException(403, "node owner/editor permission required")
    svc = GEOVisibilityService()
    await svc.sync_question_sets(db)
    result = await svc.execute(db, node_id, provider=data.get("provider", ""),
                               question_keys=data.get("question_keys"), actor_id=str(current_user.id))
    return result


@router.post("/observation-runs/{run_id}/execute")
async def execute_run(run_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Execute a prepared run (placeholder: same as create for now)."""
    r = await db.get(AIObservationRun, uuid.UUID(run_id))
    if not r: raise HTTPException(404, "run not found")
    return {"run_id": run_id, "status": r.status}


@router.get("/answers/{answer_id}")
async def get_answer(answer_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    gov = get_governance_service()
    art = await db.get(AIAnswerArtifact, uuid.UUID(answer_id))
    if not art: raise HTTPException(404, "answer not found")
    base = {"id": str(art.id), "provider": art.provider, "model": art.model,
            "captured_at": art.captured_at.isoformat() if art.captured_at else None,
            "citations": art.citations, "entity_mentions": art.entity_mentions,
            "recommendation_order": art.recommendation_order}
    if gov.is_system_admin(current_user) or gov.is_reviewer(current_user):
        base["raw_answer"] = art.raw_answer
    return base


@router.get("/visibility/{node_id}")
async def get_visibility(node_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = GEOVisibilityService()
    return await svc.get_visibility(db, node_id)


@router.get("/visibility/{node_id}/providers")
async def visibility_providers(node_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (await db.execute(select(VisibilityResult).where(VisibilityResult.node_id == node_id))).scalars().all()
    return {"providers": sorted({r.provider for r in rows})}


@router.get("/visibility/{node_id}/questions")
async def visibility_questions(node_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"node_id": node_id, "questions": await _questions_for(node_id, db)}


@router.get("/visibility/{node_id}/competitors")
async def visibility_competitors(node_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"node_id": node_id, "competitors": []}


@router.get("/visibility/{node_id}/trend")
async def visibility_trend(node_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (await db.execute(select(VisibilityResult).where(VisibilityResult.node_id == node_id)
                             .order_by(VisibilityResult.captured_at.asc()))).scalars().all()
    return {"node_id": node_id, "trend": [
        {"captured_at": r.captured_at.isoformat() if r.captured_at else None, "metric_key": r.metric_key,
         "metric_value": r.metric_value}
        for r in rows[:100]]}


async def _questions_for(node_id, db):
    return []
