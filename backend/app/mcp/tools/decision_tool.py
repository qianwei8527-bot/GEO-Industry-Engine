from sqlalchemy.ext.asyncio import AsyncSession
from app.decision.engine import DecisionEngine


class DecisionTool:
    def __init__(self, db: AsyncSession):
        self.engine = DecisionEngine(db)

    async def get_geo_score(self, company_id: str) -> dict:
        """Get GEO Score with breakdown and explanation for a company."""
        result = await self.engine.analyze_company(company_id)
        return result

    async def get_recommendation(self, company_id: str) -> list:
        """Get actionable recommendations for improving GEO visibility."""
        result = await self.engine.analyze_company(company_id)
        return result.get("recommendations", [])
    async def analyze_company(self, company_id: str) -> dict:
        return await self.engine.analyze_company(company_id)

    async def analyze_industry(self, industry_id: str) -> dict:
        return await self.engine.analyze_industry(industry_id)

    async def assess_company(self, company_id: str) -> dict:
        return await self.engine.assess_company(company_id)

