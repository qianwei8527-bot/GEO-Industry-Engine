from sqlalchemy.ext.asyncio import AsyncSession
from app.context.engine import ContextEngine


class SearchTool:
    def __init__(self, db: AsyncSession):
        self.engine = ContextEngine(db)

    async def search(self, query: str, limit: int = 10) -> dict:
        result = await self.engine.query(query, limit)
        return result.dict() if hasattr(result, "dict") else {"count": 0}
