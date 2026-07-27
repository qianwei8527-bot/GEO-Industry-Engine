from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.context.engine import ContextEngine
from app.decision.engine import DecisionEngine


class BaseAgent(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db
        self._ctx = ContextEngine(db)
        self._dec = DecisionEngine(db)

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]: pass

    @property
    @abstractmethod
    def agent_name(self) -> str: pass

    @property
    @abstractmethod
    def agent_description(self) -> str: pass

    async def get_company_context(self, company_id: str) -> Any:
        return await self._ctx.get_company_context(company_id)

    async def get_industry_context(self, industry_id: str) -> Any:
        return await self._ctx.get_industry_context(industry_id)

    async def analyze_company(self, company_id: str) -> dict:
        return await self._dec.analyze_company(company_id)

    def _format_report(self, title: str, sections: list) -> dict:
        return {"title": title, "sections": sections, "agent": self.agent_name}


class AgentRegistry:
    _agents: Dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent):
        cls._agents[agent.agent_name] = agent

    @classmethod
    def get(cls, name: str) -> Optional[BaseAgent]:
        return cls._agents.get(name)

    @classmethod
    def list_all(cls) -> List[dict]:
        return [{"name": a.agent_name, "description": a.agent_description} for a in cls._agents.values()]

    @classmethod
    def clear(cls):
        cls._agents = {}
