from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.context.engine import ContextEngine
from app.context.schemas.context_schema import CompanyContext, IndustryContext
from app.decision.models.geo_visibility import GEOVisibilityScore
from app.decision.models.industry_opportunity import IndustryOpportunityScore
from app.decision.models.company_growth import (
    CompanyGrowthScore, CompetitivePosition, GEORoadmap,
    ContentStrategy, MarketConnection,
)
from app.decision.models.capability_match import CapabilityMatchScore
from app.decision.recommendation.recommendation_engine import RecommendationEngine


class DecisionEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.context = ContextEngine(db)

    async def analyze_company(self, company_id: str) -> dict:
        ctx = await self.context.get_company_context(company_id)
        scores = {}
        scores["visibility"] = await GEOVisibilityScore().calculate(ctx)
        scores["company_growth"] = await CompanyGrowthScore().calculate(ctx)
        scores["competitive_position"] = await CompetitivePosition().calculate(ctx)
        scores["roadmap"] = await GEORoadmap().calculate(ctx)
        scores["content_strategy"] = await ContentStrategy().calculate(ctx)
        scores["market_connection"] = await MarketConnection().calculate(ctx)
        recommendations = await RecommendationEngine.generate(ctx, scores)
        return {
            "company_id": company_id,
            "company_name": ctx.company.name,
            "scores": scores,
            "overall": round(sum(s["score"] for s in scores.values()) / len(scores), 1),
            "recommendations": recommendations,
        }

    async def analyze_industry(self, industry_id: str) -> dict:
        ctx = await self.context.get_industry_context(industry_id)
        score = await IndustryOpportunityScore().calculate(ctx)
        return {
            "industry_id": industry_id,
            "industry_name": ctx.industry.name,
            "scores": {"industry_index": score},
            "company_count": len(ctx.companies),
            "capability_count": len(ctx.capabilities),
        }

    async def analyze(self, query_text: str, limit: int = 10) -> dict:
        result = await self.context.query(query_text, limit)
        return {"query": query_text, "results": result.dict()}
