from typing import Any, Dict
from agents.core.base import BaseAgent


class GEOGrowthAgent(BaseAgent):
    agent_name = "geo_growth_agent"
    agent_description = "GEO optimization roadmap, content strategy, and AI search growth suggestions"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        company_id = params.get("company_id", params.get("id"))
        ctx = await self.get_company_context(company_id)
        decision = await self.analyze_company(company_id)
        scores = decision.get("scores", {})
        roadmap = scores.get("roadmap", {})
        content = scores.get("content_strategy", {})
        market = scores.get("market_connection", {})

        sections = [
            {"heading": "GEO Optimization Roadmap",
             "content": "Priority actions to improve AI visibility",
             "actions": roadmap.get("actions", ["Complete company profile", "Add evidence"]),
             "current_score": roadmap.get("score", 0)},
            {"heading": "Content Strategy",
             "content": "Content improvements for AI search",
             "actions": content.get("actions", ["Add detailed capability descriptions"])},
            {"heading": "Market Connection",
             "content": "Partnership and ecosystem opportunities",
             "actions": market.get("actions", ["Explore industry partnerships"])},
            {"heading": "Current Scores",
             "metrics": {k: v.get("score", 0) for k, v in scores.items()}},
        ]
        return self._format_report(f"GEO Growth Plan: {ctx.company.name}", sections)
