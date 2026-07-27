from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from app.models.relationship import Relationship
from app.models.entity import Entity


class RelationshipRetriever:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_relationships(self, entity_id: str) -> List[Relationship]:
        stmt = select(Relationship).where(
            or_(
                Relationship.source_id == entity_id,
                Relationship.target_id == entity_id,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_entity_name(self, entity_id: str) -> str:
        stmt = select(Entity.name).where(Entity.id == entity_id)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return row or "Unknown"

    async def get_entity_type(self, entity_id: str) -> str:
        stmt = select(Entity.entity_type).where(Entity.id == entity_id)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return row or "unknown"
