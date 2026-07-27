from typing import Optional
from agents.core.base import AgentRegistry


class IntentRouter:
    @staticmethod
    def route(query: str) -> Optional[str]:
        q = query.lower()
        if any(w in q for w in ["industrie", "industry", "branche", "趋势", "结构"]):
            return "industry_agent"
        if any(w in q for w in ["company", "enterprise", "firma", "企业", "公司"]):
            return "company_agent"
        if any(w in q for w in ["geo", "visibility", "score", "ranking", "优化", "增长"]):
            return "geo_growth_agent"
        return "analyst_agent"

    @staticmethod
    def available_agents() -> list:
        return AgentRegistry.list_all()
