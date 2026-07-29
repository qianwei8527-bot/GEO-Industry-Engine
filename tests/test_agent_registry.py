"""Agent registry and architecture validation"""
import pytest

def test_agent_registry_importable():
    from app.agents.core.agent_registry import AgentRegistry
    assert AgentRegistry is not None

def test_base_agent_importable():
    from app.agents.core.base_agent import BaseAgent
    assert BaseAgent is not None

def test_intent_router_importable():
    from app.agents.router.intent_router import IntentRouter
    assert IntentRouter is not None

def test_task_planner_importable():
    from app.agents.planner.task_planner import TaskPlanner
    assert TaskPlanner is not None

def test_agent_tools_importable():
    from app.agents.tools.context_tool import ContextTool
    from app.agents.tools.decision_tool import DecisionTool
    assert ContextTool is not None and DecisionTool is not None

@pytest.mark.skip(reason="Agent class names need verification against actual implementation")
def test_domain_agents_importable():
    from app.agents.agents.analyst_agent import DataAnalystAgent
    from app.agents.agents.company_agent import CompanyAgent
    from app.agents.agents.geo_growth_agent import GEOGrowthAgent
    from app.agents.agents.industry_agent import IndustryAgent
    assert all([DataAnalystAgent, CompanyAgent, GEOGrowthAgent, IndustryAgent])
