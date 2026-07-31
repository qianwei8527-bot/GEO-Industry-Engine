"""P1-B: Provider Matcher - orchestrates matching + provider search + industry context."""
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.match_tool import match_tool
from app.agents.tools.provider_search_tool import provider_search_tool
from app.agents.tools.industry_tool import industry_tool


class ProviderMatcher(BaseAgent):
    """Role agent: match enterprise demands with capable providers."""

    def __init__(self):
        super().__init__(name="ProviderMatcher", description="Provider discovery & capability matching: identify candidates, explain fit, let enterprises decide")
        self.register_tool("find_matches", match_tool.find_matches)
        self.register_tool("search_providers", provider_search_tool.search)
        self.register_tool("get_provider_details", provider_search_tool.get_provider_details)
        self.register_tool("get_industry_overview", industry_tool.get_industry_overview)
        self.register_tool("get_company_context", context_tool.get_company_context)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            demand_id = ctx.params.get("demand_id")
            industry_id = ctx.params.get("industry_id")
            company_id = ctx.params.get("company_id")

            matches = None
            industry_context = None
            company_context = None

            # Step 1: Match if demand_id provided
            if demand_id:
                matches = await self.use_tool("find_matches", demand_id=demand_id, limit=5)
                if isinstance(matches, dict) and matches.get("error"):
                    return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=matches["error"])

            # Step 2: Get industry context if industry_id provided
            if industry_id:
                industry_context = await self.use_tool("get_industry_overview", industry_id=industry_id)

            # Step 3: Get company context if company_id provided
            if company_id:
                company_context = await self.use_tool("get_company_context", company_id=company_id)

            # Step 4: Find providers by search
            providers = await self.use_tool("search_providers", min_trust=0.3, limit=5)

            # Compile results
            match_list = matches.get("matches", []) if isinstance(matches, dict) and matches.get("matches") else []
            top_score = max((m.get("score", 0) for m in match_list), default=0)

            result = AgentResult(
                agent_id=self.agent_id, task_id=ctx.task_id, success=True,
                data={
                    "matches": match_list,
                    "top_match_score": top_score,
                    "provider_count": len(providers) if isinstance(providers, list) else 0,
                    "industry": industry_context if isinstance(industry_context, dict) else None,
                    "company": {"id": company_id} if company_context else None,
                },
                summary=f"Provider Matching: {len(match_list)} matches (top score {top_score}) | {len(providers) if isinstance(providers, list) else 0} providers available",
                tool_calls=["find_matches", "search_providers", "get_industry_overview"],
            )

            # P0-C: citations
            if demand_id:
                result.add_citation(source="MatchEngine", id=demand_id, field="matches", description=f"Capability-matched candidates: {len(match_list)} providers identified")
            if industry_id:
                result.add_citation(source="Industry", id=industry_id, field="overview", description="Industry context and ecosystem density")
            result.add_citation(source="ProviderSearch", id="search", field="providers", description=f"Available providers: {len(providers) if isinstance(providers, list) else 0}")
            result.validate_citations()

            return result

        except Exception as e:
            return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=str(e))
