"""C6.6 Memory Universe API — unified node memory timeline, causes, narrative."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.memory_universe import MemoryUniverseService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/universe/memory", tags=["memory-universe"])


@router.get("/timeline/{node_id}")
async def timeline(node_id: str, limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return await MemoryUniverseService().unified_timeline(db, node_id, limit)


@router.get("/causes/{node_id}")
async def causes(node_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await MemoryUniverseService().cause_analysis(db, node_id)


@router.get("/story/{node_id}")
async def story(node_id: str, name: str = Query("", description="节点名称"), db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return await MemoryUniverseService().generate_narrative(db, node_id, name)
