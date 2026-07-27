from typing import Any, Dict
from agents.core.base import BaseAgent


class CompanyAgent(BaseAgent):
    agent_name = "company_agent"
    agent_description = "Company profile, strengths, weaknesses, and competitive positioning"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        company_id = params.get("company_id", params.get("id"))
        ctx = await self.get_company_context(company_id)
        decision = await self.analyze_company(company_id)
        scores = decision.get("scores", {})
        recs = decision.get("recommendations", [])
        sections = [
            {"heading": "Company Profile", "content": ctx.company.name,
             "metrics": {"industry": [i.name for i in ctx.industries],
                         "verified": ctx.company.is_verified,
                         "subscription": ctx.company.subscription_tier}},
            {"heading": "Performance Scores",
             "content": "GEO and Trust scores",
             "metrics": {"visibility": scores.get("visibility", {}).get("score", 0),
                         "growth": scores.get("company_growth", {}).get("score", 0),
                         "competitive": scores.get("competitive_position", {}).get("score", 0),
                         "trust": ctx.scoring.trust_score,
                         "geo": ctx.scoring.geo_score}},
            {"heading": "Capabilities",
             "content": f"{len(ctx.capabilities)} capabilities documented",
             "items": [{"name": c.name, "level": c.level} for c in ctx.capabilities]},
            {"heading": "Recommendations",
             "content": f"{len(recs)} recommendations",
             "items": [{"type": r.get("type"), "priority": r.get("priority"),
                        "title": r.get("title"), "reason": r.get("reason")} for r in recs]},
        ]
        return self._format_report(f"Company Intelligence: {ctx.company.name}", sections)
