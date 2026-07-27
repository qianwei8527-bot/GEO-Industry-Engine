from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models.entity import Entity
from app.schemas.entity import EntityResponse

router = APIRouter(prefix="/api/v1/entities", tags=["entities"])

@router.get("/", response_model=List[EntityResponse])
async def list_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Entity).offset(skip).limit(limit)
    if entity_type:
        stmt = stmt.where(Entity.entity_type == entity_type)
    result = await db.execute(stmt)
    return [EntityResponse.model_validate(e) for e in result.scalars().all()]

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Entity).where(Entity.id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntityResponse.model_validate(entity)
