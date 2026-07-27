from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models.relationship import Relationship
from app.schemas.relationship import RelationshipCreate, RelationshipResponse

router = APIRouter(prefix="/api/v1/relationships", tags=["relationships"])

@router.post("/", response_model=RelationshipResponse, status_code=201)
async def create_relationship(data: RelationshipCreate, db: AsyncSession = Depends(get_db)):
    rel = Relationship(**data.model_dump())
    db.add(rel)
    await db.commit()
    await db.refresh(rel)
    return RelationshipResponse.model_validate(rel)

@router.get("/", response_model=List[RelationshipResponse])
async def list_relationships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source_id: str = Query(None),
    target_id: str = Query(None),
    relation_type: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Relationship).offset(skip).limit(limit)
    if source_id:
        stmt = stmt.where(Relationship.source_id == source_id)
    if target_id:
        stmt = stmt.where(Relationship.target_id == target_id)
    if relation_type:
        stmt = stmt.where(Relationship.relation_type == relation_type)
    result = await db.execute(stmt)
    return [RelationshipResponse.model_validate(r) for r in result.scalars().all()]

@router.get("/{rel_id}", response_model=RelationshipResponse)
async def get_relationship(rel_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Relationship).where(Relationship.id == rel_id))
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return RelationshipResponse.model_validate(rel)
