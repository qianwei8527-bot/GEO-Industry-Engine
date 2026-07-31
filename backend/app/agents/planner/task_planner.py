# GEO-Industry-Engine Task Planner - P0-A: produces TaskStep definitions for TaskExecutor
from typing import List, Dict
from app.agents.core.base_agent import AgentContext
from app.agents.executor.task_executor import TaskStep


class TaskPlanner:
    """Decomposes user intent into DAG-executable TaskSteps."""

    def plan(self, ctx: AgentContext) -> List[TaskStep]:
        """Produce ordered TaskStep list from AgentContext."""
        steps = []

        # Step 1: Always get context first
        steps.append(TaskStep(
            id="context_lookup",
            agent_name="CompanyIntelligence",
            tool_name="get_company_context",
            params={"company_id": ctx.params.get("company_id")},
            description="Retrieve company context from knowledge graph",
            critical=True,
        ))

        # Step 2: Get GEO scores (depends on context)
        steps.append(TaskStep(
            id="geo_scoring",
            agent_name="CompanyIntelligence",
            tool_name="get_geo_score",
            params={"company_id": ctx.params.get("company_id")},
            depends_on=["context_lookup"],
            description="Calculate GEO scores via Decision Engine",
            critical=True,
        ))

        # Step 3: Get growth opportunities (can run parallel with scoring)
        steps.append(TaskStep(
            id="growth_opportunities",
            agent_name="GEOGrowth",
            tool_name="get_opportunity",
            params={"company_id": ctx.params.get("company_id")},
            depends_on=["context_lookup"],
            description="Identify GEO growth opportunities",
            critical=True,
        ))

        # Step 4: Get strategic roadmap
        steps.append(TaskStep(
            id="strategic_roadmap",
            agent_name="GEOGrowth",
            tool_name="get_roadmap",
            params={"company_id": ctx.params.get("company_id")},
            depends_on=["geo_scoring", "growth_opportunities"],
            description="Generate strategic growth roadmap",
            critical=False,
        ))

        # Step 5: Search for related entities (can run parallel)
        steps.append(TaskStep(
            id="entity_search",
            agent_name="DataAnalyst",
            tool_name="search",
            params={"query": ctx.input_query, "limit": 5},
            description="Search for related entities in knowledge graph",
            critical=False,
        ))

        return steps

    def plan_simple(self, ctx: AgentContext) -> List[TaskStep]:
        """Simple fallback: single step plan."""
        intent_to_agent = {
            "company": "CompanyIntelligence",
            "industry": "IndustryAnalyst",
            "geo_growth": "GEOGrowth",
            "analyze": "DataAnalyst",
        }
        agent_name = intent_to_agent.get(ctx.intent, "CompanyIntelligence")
        tool_name = {
            "industry": "get_industry_context",
            "company": "get_company_context",
            "geo_growth": "get_company_context",
            "analyze": "search",
        }.get(ctx.intent, "get_company_context")

        return [TaskStep(
            id="single_step",
            agent_name=agent_name,
            tool_name=tool_name,
            params=ctx.params or {"query": ctx.input_query},
            description=f"Execute {ctx.intent} analysis",
            critical=True,
        )]


task_planner = TaskPlanner()
