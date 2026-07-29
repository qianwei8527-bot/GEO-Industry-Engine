from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.context.retrieval.entity_retriever import EntityRetriever
from app.context.schemas.context_schema import (
    IndustryContext, IndustryProfile, CompanyBrief,
    CapabilityInfo, TrendInfo, EventInfo, OpportunityInfo
)
from app.models.company import Company
from app.models.event import Event


class IndustryContextBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.entity = EntityRetriever(db)

    async def build(self, industry_id: str) -> IndustryContext:
        industry = await self.entity.get_industry(industry_id)
        if not industry:
            return IndustryContext(industry=IndustryProfile(id=industry_id, name="", code="", level=0))

        profile = IndustryProfile(
            id=industry.id, name=industry.name, code=industry.code,
            level=industry.level, description=industry.description,
            parent_id=industry.parent_id,
        )

        # Companies in this industry
        companies = await self.entity.get_companies_by_industry(industry_id)
        company_briefs = [
            CompanyBrief(id=c.id, name=c.name, geo_score=c.geo_score or 0, is_verified=c.is_verified)
            for c in companies
        ]

        # Capabilities across companies
        from app.models.capability import Capability
        stmt = select(Capability).where(Capability.company_id.in_([c.id for c in companies])).limit(50)
        result = await self.db.execute(stmt)
        caps = [
            CapabilityInfo(id=cap.id, name=cap.name, level=cap.level, category=cap.category)
            for cap in result.scalars().all()
        ]

        # Events for companies in this industry
        stmt = select(Event).where(Event.entity_id.in_([c.id for c in companies])).order_by(Event.event_date.desc()).limit(20)
        result = await self.db.execute(stmt)
        events = [
            EventInfo(id=e.id, event_type=e.event_type, title=e.title,
                      event_date=e.event_date, description=e.description,
                      impact=e.impact)
            for e in result.scalars().all()
        ]

        return IndustryContext(
            industry=profile, companies=company_briefs,
            capabilities=caps, trends=[],
            events=events, opportunities=[],
        )
