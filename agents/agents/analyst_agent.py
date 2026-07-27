from typing import Any, Dict
from agents.core.base_agent import BaseAgent
from app.context.engine import ContextEngine


class AnalystAgent(BaseAgent):
    agent_name = "analyst_agent"
    agent_description = "Data intelligence: finds missing entities, capabilities, relationships, and evidence"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ctx_engine = ContextEngine(self.db)
        gaps = []
        query = params.get("query", "")
        result = await ctx_engine.query(query, limit=5) if query else None

        if result and result.results:
            for c in result.results:
                company_ctx = await self.get_company_context(str(c.id))
                if len(company_ctx.capabilities) < 2:
                    gaps.append({"entity": c.name, "type": "missing_capabilities",
                                 "detail": f"Only {len(company_ctx.capabilities)} capabilities"})
                if len(company_ctx.evidence) < 1:
                    gaps.append({"entity": c.name, "type": "missing_evidence",
                                 "detail": "No evidence documents found"})

        sections = [
            {"heading": "Data Gap Analysis",
             "content": f"Found {len(gaps)} data gaps",
             "items": gaps[:20]},
        ]
        return self._format_report("Data Intelligence Report", sections)
