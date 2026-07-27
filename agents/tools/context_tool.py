from sqlalchemy.ext.asyncio import AsyncSession
from app.context.engine import ContextEngine


class ContextTool:
    def __init__(self, db: AsyncSession):
        self.engine = ContextEngine(db)

    async def get_company_context(self, company_id: str) -> dict:
        result = await self.engine.get_company_context(company_id)
        return result.dict() if hasattr(result, "dict") else result

    async def get_industry_context(self, industry_id: str) -> dict:
        result = await self.engine.get_industry_context(industry_id)
        return result.dict() if hasattr(result, "dict") else result
