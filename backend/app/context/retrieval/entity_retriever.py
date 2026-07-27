from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
import uuid
from app.models.company import Company
from app.models.entity import Entity
from app.models.industry import Industry
from app.models.capability import Capability


class EntityRetriever:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_company(self, company_id: str) -> Optional[Company]:
        stmt = select(Company).where(Company.id == company_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_company_by_name(self, name: str) -> Optional[Company]:
        stmt = select(Company).where(Company.name.ilike(f"%{name}%"))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_industry(self, industry_id: str) -> Optional[Industry]:
        stmt = select(Industry).where(Industry.id == industry_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_companies(self, query: str, limit: int = 20) -> List[Company]:
        stmt = select(Company).where(
            or_(
                Company.name.ilike(f"%{query}%"),
                Company.description.ilike(f"%{query}%"),
            )
        ).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_companies_by_industry(self, industry_id: str) -> List[Company]:
        stmt = select(Company).where(Company.industry_id == industry_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_capability(self, capability_id: str) -> Optional[Capability]:
        stmt = select(Capability).where(Capability.id == capability_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_capabilities_by_company(self, company_id: str) -> List[Capability]:
        stmt = select(Capability).where(Capability.company_id == company_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
