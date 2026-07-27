from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.context.builders.company_context import CompanyContextBuilder
from app.context.builders.industry_context import IndustryContextBuilder
from app.context.builders.capability_context import CapabilityContextBuilder
from app.context.schemas.context_schema import (
    CompanyContext, IndustryContext, CapabilityContext,
    ContextQueryRequest, ContextQueryResponse, CompanyBrief
)
from app.context.retrieval.entity_retriever import EntityRetriever
from app.context.ranking.relevance import RelevanceScorer


class ContextEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_company_context(self, company_id: str) -> CompanyContext:
        builder = CompanyContextBuilder(self.db)
        return await builder.build(company_id)

    async def get_industry_context(self, industry_id: str) -> IndustryContext:
        builder = IndustryContextBuilder(self.db)
        return await builder.build(industry_id)

    async def get_capability_context(self, capability_id: str) -> CapabilityContext:
        builder = CapabilityContextBuilder(self.db)
        return await builder.build(capability_id)

    async def query(self, query_text: str, limit: int = 10, entity_type: Optional[str] = None) -> ContextQueryResponse:
        retriever = EntityRetriever(self.db)
        companies = await retriever.search_companies(query_text, limit=limit * 2)
        if entity_type == "company":
            companies = [c for c in companies if c.entity_type == "company"]

        scorer = RelevanceScorer()
        scored = scorer.score_companies(query_text, companies)
        top = [c for c, s in scored[:limit]]

        return ContextQueryResponse(
            query=query_text,
            results=[CompanyBrief(id=c.id, name=c.name, geo_score=c.geo_score or 0, is_verified=c.is_verified) for c in top],
            total=len(top),
        )
