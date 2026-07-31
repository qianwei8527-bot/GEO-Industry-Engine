"""P1-B: Enterprise Diagnostician - orchestrates CompanyIntelligence + GEOGrowth + Evidence."""
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.decision_tool import decision_tool
from app.agents.tools.evidence_tool import evidence_tool
from app.agents.tools.provider_search_tool import provider_search_tool
from app.agents.reporting import ReportGenerator


class EnterpriseDiagnostician(BaseAgent):
    """Role agent: full enterprise GEO diagnosis for company users."""

    def __init__(self):
        super().__init__(name="EnterpriseDiagnostician", description="Enterprise GEO diagnosis: scoring, trust verification, provider discovery")
        self.register_tool("get_company_context", context_tool.get_company_context)
        self.register_tool("get_geo_score", decision_tool.get_geo_score)
        self.register_tool("get_evidence", evidence_tool.get_evidence)
        self.register_tool("search_providers", provider_search_tool.search)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            cid = ctx.params.get("company_id")
            if not cid:
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error="Missing company_id")

            # Step 1: Company context + geo score (parallel conceptually, but tools are sequential)
            context = await self.use_tool("get_company_context", company_id=cid)
            if isinstance(context, dict) and context.get("error"):
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=context["error"])

            score = await self.use_tool("get_geo_score", company_id=cid)
            if isinstance(score, dict) and score.get("error"):
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=score["error"])

            # Step 2: Evidence verification
            evidence = await self.use_tool("get_evidence", entity_id=cid)

            # Step 3: Find relevant providers
            providers = await self.use_tool("search_providers", min_trust=0.5, limit=5)

            # Step 4: Generate strategic report
            report = ReportGenerator.generate(context, score)

            result = AgentResult(
                agent_id=self.agent_id, task_id=ctx.task_id, success=True,
                data={
                    "report": {
                        "company_name": report.company_name,
                        "geo_identity": report.geo_identity,
                        "geo_score": {"overall": score.get("overall", 0)},
                        "visibility": report.visibility_assessment,
                        "trust": report.trust_assessment,
                        "capability": report.capability_profile,
                        "evidence_summary": evidence.get("trust_level", "N/A") if isinstance(evidence, dict) else "N/A",
                        "candidate_providers": providers if isinstance(providers, list) else [],
                        "opportunities": report.opportunities,
                        "risks": report.risks,
                        "recommendations": report.strategic_recommendations,
                    },
                },
                summary=f"Enterprise Diagnosis: {report.company_name} | GEO {score.get('overall', 0)} | Trust {evidence.get('trust_level', '?') if isinstance(evidence, dict) else '?'}",
                tool_calls=["get_company_context", "get_geo_score", "get_evidence", "search_providers"],
            )

            # P0-C: citations
            result.add_citation(source="Entity", id=cid, field="profile", description="Company identity from knowledge graph")
            result.add_citation(source="DecisionEngine", id=cid, field="scores", description="GEO scoring from Decision Engine")
            result.add_citation(source="Evidence", id=cid, field="confidence_levels", description=f"Evidence verification: {evidence.get('total_evidence', 0) if isinstance(evidence, dict) else 0} records")
            result.add_citation(source="ProviderSearch", id="search", field="providers", description=f"Candidate providers: {len(providers) if isinstance(providers, list) else 0} identified")
            result.validate_citations()

            return result

        except Exception as e:
            return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=str(e))
