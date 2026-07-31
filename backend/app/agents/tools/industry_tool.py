"""P1-A: Industry tool for agents - industry-level insights."""
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid


class IndustryTool:
    """Provides industry-level context and analytics for agents."""

    def __init__(self):
        self._db = None

    def set_db(self, db: AsyncSession):
        self._db = db

    async def get_industry_overview(self, industry_id: str) -> dict:
        """Get comprehensive industry overview with company/provider statistics."""
        from app.models.industry import Industry
        from app.models.company import Company
        from app.models.provider import Provider

        uid = uuid.UUID(industry_id)

        # Industry info
        ind_result = await self._db.execute(select(Industry).where(Industry.id == uid))
        industry = ind_result.scalar_one_or_none()
        if not industry:
            return {"error": f"Industry {industry_id} not found"}

        # Company count
        comp_count = await self._db.execute(
            select(func.count()).select_from(Company).where(Company.industry_id == uid)
        )
        company_count = comp_count.scalar() or 0

        # Provider count (through entity relationship)
        from app.models.entity import Entity
        prov_count = await self._db.execute(
            select(func.count()).select_from(Provider).join(Entity, Provider.entity_id == Entity.id)
            .where(Entity.industry_id == uid)
        )
        provider_count = prov_count.scalar() or 0

        # Average GEO scores
        avg_geo = await self._db.execute(
            select(func.avg(Company.geo_score)).where(Company.industry_id == uid)
        )
        avg_geo_score = round(avg_geo.scalar() or 0, 1)

        return {
            "industry_id": str(industry_id),
            "name": industry.name,
            "description": industry.description[:200] if industry.description else "",
            "company_count": company_count,
            "provider_count": provider_count,
            "avg_geo_score": avg_geo_score,
            "maturity": "growing" if company_count < 10 else "established" if company_count < 100 else "mature",
        }

    async def get_industry_companies(self, industry_id: str, limit: int = 10) -> list:
        """Get list of companies in an industry with GEO scores."""
        from app.models.company import Company

        uid = uuid.UUID(industry_id)
        result = await self._db.execute(
            select(Company).where(Company.industry_id == uid).order_by(Company.geo_score.desc()).limit(limit)
        )
        rows = result.scalars().all()

        return [{"id": str(r.id), "name": r.name, "geo_score": r.geo_score, "is_verified": r.is_verified} for r in rows]

    async def get_top_industries(self, limit: int = 5) -> list:
        """Get industries ranked by company count (ecosystem density)."""
        from app.models.industry import Industry
        from app.models.company import Company
        from sqlalchemy import func

        result = await self._db.execute(
            select(Industry.name, func.count(Company.id).label("count"))
            .join(Company, Company.industry_id == Industry.id, isouter=True)
            .group_by(Industry.id, Industry.name)
            .order_by(func.count(Company.id).desc())
            .limit(limit)
        )
        return [{"name": r[0], "company_count": r[1]} for r in result.all()]


industry_tool = IndustryTool()
