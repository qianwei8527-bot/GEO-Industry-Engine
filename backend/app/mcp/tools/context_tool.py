from sqlalchemy.ext.asyncio import AsyncSession
from app.context.engine import ContextEngine


class ContextTool:
    def __init__(self, db: AsyncSession):
        self.engine = ContextEngine(db)

    async def get_company_context(self, company_id: str) -> dict:
        """Get full company context with capabilities, relationships, events, and scores."""
        result = await self.engine.get_company_context(company_id)
        return result.dict()

    async def get_industry_context(self, industry_id: str) -> dict:
        """Get industry context with companies, capabilities, and events."""
        result = await self.engine.get_industry_context(industry_id)
        return result.dict()
