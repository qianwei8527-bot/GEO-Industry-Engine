from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.context.engine import ContextEngine
from app.decision.engine import DecisionEngine


class BaseAgent(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db
        self._context_engine = ContextEngine(db)
        self._decision_engine = DecisionEngine(db)

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def agent_name(self) -> str:
        pass

    @property
    @abstractmethod
    def agent_description(self) -> str:
        pass

    async def get_company_context(self, company_id: str) -> Any:
        return await self._context_engine.get_company_context(company_id)

    async def get_industry_context(self, industry_id: str) -> Any:
        return await self._context_engine.get_industry_context(industry_id)

    async def analyze_company(self, company_id: str) -> dict:
        return await self._decision_engine.analyze_company(company_id)

    def _format_report(self, title: str, sections: list) -> dict:
        return {"title": title, "sections": sections, "agent": self.agent_name}
