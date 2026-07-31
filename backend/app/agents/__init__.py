from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.core.agent_registry import registry
from app.agents.agents.industry_agent import IndustryAnalystAgent
from app.agents.agents.company_agent import CompanyIntelligenceAgent
from app.agents.agents.geo_growth_agent import GEOGrowthAgent
from app.agents.agents.analyst_agent import DataAnalystAgent
from app.agents.agents.enterprise_diagnostician import EnterpriseDiagnostician
from app.agents.agents.provider_matcher import ProviderMatcher
from app.agents.agents.observation_agent import GEOObservationAgent
from app.agents.router.intent_router import intent_router
from app.agents.planner.task_planner import task_planner
from app.agents.executor.task_executor import TaskExecutor, TaskStep, ExecutionPlan, task_executor

# Auto-register base agents
registry.register(IndustryAnalystAgent())
registry.register(CompanyIntelligenceAgent())
registry.register(GEOGrowthAgent())
registry.register(DataAnalystAgent())

# P1-B: Register role agents
registry.register(EnterpriseDiagnostician())
registry.register(ProviderMatcher())
# Sprint 4.0: Register observation agent
registry.register(GEOObservationAgent())

__all__ = ['BaseAgent', 'AgentContext', 'AgentResult', 'registry', 'intent_router',
           'task_planner', 'TaskExecutor', 'TaskStep', 'ExecutionPlan', 'task_executor']
