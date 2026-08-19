"""C8.3 World State Transition API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.world_transition import get_world_transition_service

router = APIRouter(prefix="/api/v1/universe/world-state/transitions", tags=["world-transition"])


@router.post("/generate")
async def generate_transition(data: dict, db: AsyncSession = Depends(get_db)):
    svc = get_world_transition_service()
    try:
        return await svc.generate(db, data.get("from_snapshot_id", ""), data.get("to_snapshot_id", ""))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("")
async def list_transitions(limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    return {"transitions": await get_world_transition_service().list_transitions(db, limit)}


@router.get("/compatibility")
async def compatibility(from_snapshot_id: str = Query(...), to_snapshot_id: str = Query(...),
                        db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_transition_service().compatibility(db, from_snapshot_id, to_snapshot_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{transition_id}")
async def get_transition(transition_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_transition_service().get(db, transition_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{transition_id}/changes")
async def transition_changes(transition_id: str, change_type: str = Query(None),
                             concept_code: str = Query(None), db: AsyncSession = Depends(get_db)):
    try:
        changes = await get_world_transition_service().changes(db, transition_id, change_type, concept_code)
        return {"changes": changes, "count": len(changes)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{transition_id}/gaps")
async def transition_gaps(transition_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return {"gap_lifecycle": await get_world_transition_service().gap_lifecycle(db, transition_id)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{transition_id}/source-chain")
async def transition_source_chain(transition_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_transition_service().source_chain(db, transition_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{transition_id}/integrity")
async def transition_integrity(transition_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_transition_service().integrity(db, transition_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
