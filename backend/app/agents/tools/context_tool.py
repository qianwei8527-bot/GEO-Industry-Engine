from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class ContextTool:
    def __init__(self):
        self._engine = None

    def set_db(self, db: AsyncSession):
        self._engine = None  # Will be recreated per request
        self._db = db

    async def get_company_context(self, company_id: str) -> dict:
        from app.context.engine import ContextEngine
        try:
            engine = ContextEngine(self._db)
            return await engine.get_company_context(company_id)
        except Exception as e:
            return {'error': str(e)}

    async def get_industry_context(self, industry_id: str) -> dict:
        from app.context.engine import ContextEngine
        try:
            engine = ContextEngine(self._db)
            return await engine.get_industry_context(industry_id)
        except Exception as e:
            return {'error': str(e)}

    async def search(self, query: str, limit: int = 5) -> list:
        from app.context.engine import ContextEngine
        try:
            engine = ContextEngine(self._db)
            return await engine.query(query, limit)
        except Exception as e:
            return [{'error': str(e)}]

context_tool = ContextTool()
