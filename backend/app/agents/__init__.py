from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.core.agent_registry import registry
from app.agents.agents.industry_agent import IndustryAnalystAgent
from app.agents.agents.company_agent import CompanyIntelligenceAgent
from app.agents.agents.geo_growth_agent import GEOGrowthAgent
from app.agents.agents.analyst_agent import DataAnalystAgent
from app.agents.router.intent_router import intent_router
from app.agents.planner.task_planner import task_planner

# Auto-register agents
registry.register(IndustryAnalystAgent())
registry.register(CompanyIntelligenceAgent())
registry.register(GEOGrowthAgent())
registry.register(DataAnalystAgent())

__all__ = ['BaseAgent','AgentContext','AgentResult','registry','intent_router','task_planner']