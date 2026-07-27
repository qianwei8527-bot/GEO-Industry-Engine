from typing import Any, Dict
from agents.core.base_agent import BaseAgent


class IndustryAgent(BaseAgent):
    agent_name = "industry_agent"
    agent_description = "Industry structure analysis, trends, and opportunity identification"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        industry_id = params.get("industry_id", params.get("id"))
        ctx = await self.get_industry_context(industry_id)
        sections = [
            {"heading": "Industry Overview", "content": ctx.industry.name,
             "metrics": {"code": ctx.industry.code, "level": ctx.industry.level,
                         "companies": len(ctx.companies), "capabilities": len(ctx.capabilities),
                         "events": len(ctx.events)}},
            {"heading": "Key Companies",
             "content": f"Total companies in this industry: {len(ctx.companies)}",
             "items": [{"id": str(c.id), "name": c.name, "geo_score": c.geo_score} for c in ctx.companies[:10]]},
            {"heading": "Recent Events",
             "content": f"Recent events: {len(ctx.events)}",
             "items": [{"title": e.title, "type": e.event_type, "date": str(e.occurred_at)[:10]} for e in ctx.events[:10]]},
        ]
        return self._format_report(f"Industry Analysis: {ctx.industry.name}", sections)
