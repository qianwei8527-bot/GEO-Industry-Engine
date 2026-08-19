"""C7 Demand Intelligence API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.demand_intelligence import get_demand_intelligence_service

router = APIRouter(prefix="/api/v1/universe/demand", tags=["demand"])


@router.post("/events")
async def create_demand_event(data: dict, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    """Create a DemandEvent. Actor comes from the authenticated session."""
    svc = get_demand_intelligence_service()
    try:
        return await svc.create_event(db, data, str(current_user.id), current_user.name)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/events")
async def list_demand_events(limit: int = Query(50, ge=1, le=200),
                             db: AsyncSession = Depends(get_db)):
    svc = get_demand_intelligence_service()
    events = await svc.list_events(db, limit)
    return {"count": len(events), "events": events}


@router.post("/events/{event_id}/analyze")
async def analyze_demand(event_id: str, db: AsyncSession = Depends(get_db)):
    """Demand Gap Analysis: match nodes with capability + evidence + reputation."""
    svc = get_demand_intelligence_service()
    try:
        return await svc.analyze(db, event_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

# ---- C7.4 Demand Driven Connection ----

@router.post("/candidates/generate")
async def generate_candidates(data: dict, db: AsyncSession = Depends(get_db)):
    """Project DemandEvent gap into ConnectionCandidates (idempotent)."""
    from app.services.demand_connection import get_demand_connection_service
    svc = get_demand_connection_service()
    try:
        return await svc.generate(db, data.get("demand_event_id", ""))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/candidates")
async def list_candidates(demand_event_id: str = Query(None),
                          limit: int = Query(100, ge=1, le=500),
                          db: AsyncSession = Depends(get_db)):
    from app.services.demand_connection import get_demand_connection_service
    svc = get_demand_connection_service()
    candidates = await svc.list(db, demand_event_id, limit)
    return {"count": len(candidates), "candidates": candidates}


@router.get("/candidates/boundary")
async def candidate_boundary(db: AsyncSession = Depends(get_db)):
    from app.services.demand_connection import get_demand_connection_service
    return await get_demand_connection_service().boundary(db)

@router.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    from app.services.demand_connection import get_demand_connection_service
    svc = get_demand_connection_service()
    try:
        return await svc.get(db, candidate_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/candidates/{candidate_id}/decision")
async def decide_candidate(candidate_id: str, data: dict,
                           db: AsyncSession = Depends(get_db)):
    from app.services.demand_connection import get_demand_connection_service
    svc = get_demand_connection_service()
    try:
        return await svc.decide(
            db, candidate_id,
            data.get("decision", ""),
            source=data.get("decision_source", "rule"),
            actor=data.get("actor"),
            reason=data.get("reason"),
            scope=data.get("decision_scope", "production"),
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/candidates/{candidate_id}/outcome")
async def record_outcome(candidate_id: str, data: dict,
                         db: AsyncSession = Depends(get_db)):
    from app.services.demand_connection import get_demand_connection_service
    svc = get_demand_connection_service()
    try:
        return await svc.record_outcome(db, candidate_id, data.get("outcome", ""), actor=data.get("actor"))
    except ValueError as e:
        raise HTTPException(400, str(e))

