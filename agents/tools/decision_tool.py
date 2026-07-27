from sqlalchemy.ext.asyncio import AsyncSession
from app.decision.engine import DecisionEngine


class DecisionTool:
    def __init__(self, db: AsyncSession):
        self.engine = DecisionEngine(db)

    async def analyze_company(self, company_id: str) -> dict:
        return await self.engine.analyze_company(company_id)
