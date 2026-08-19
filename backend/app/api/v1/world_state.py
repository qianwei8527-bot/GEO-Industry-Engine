"""C8.2 World State API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.world_state import get_world_state_service

router = APIRouter(prefix="/api/v1/universe/world-state", tags=["world-state"])


@router.post("/generate")
async def generate_state(data: dict, db: AsyncSession = Depends(get_db)):
    svc = get_world_state_service()
    try:
        return await svc.generate(
            db, data.get("world_code", ""), data.get("world_version", ""),
            data.get("state_scope", "production"), data.get("projection_as_of"),
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/snapshots")
async def list_snapshots(limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    return {"snapshots": await get_world_state_service().list_snapshots(db, limit)}


@router.get("/{snapshot_id}")
async def get_snapshot(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_state_service().get(db, snapshot_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{snapshot_id}/summary")
async def snapshot_summary(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_state_service().summary(db, snapshot_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{snapshot_id}/concepts/{concept_code}")
async def concept_state(snapshot_id: str, concept_code: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_state_service().concept_state(db, snapshot_id, concept_code)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{snapshot_id}/gaps")
async def snapshot_gaps(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return {"gaps": await get_world_state_service().gaps(db, snapshot_id)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{snapshot_id}/unknown")
async def snapshot_unknown(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_state_service().unknown_excluded(db, snapshot_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{snapshot_id}/source-chain")
async def snapshot_source_chain(snapshot_id: str, entity_id: str = Query(...),
                                concept_code: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_state_service().source_chain(db, snapshot_id, entity_id, concept_code)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{snapshot_id}/integrity")
async def snapshot_integrity(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_world_state_service().check_integrity(db, snapshot_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
