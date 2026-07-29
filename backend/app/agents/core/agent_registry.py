# 参考: CrewAI Agent Registry + Dify Agent 注册模式
from typing import Dict, List, Optional, Type
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult

class AgentRegistry:
    _instance = None
    _agents: Dict[str, BaseAgent] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, agent: BaseAgent):
        self._agents[agent.name] = agent
        return agent

    def unregister(self, name: str):
        return self._agents.pop(name, None)

    def get(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

    def list_all(self) -> Dict[str, str]:
        return {name: a.description for name, a in self._agents.items()}

    def find_by_intent(self, intent: str) -> List[BaseAgent]:
        intent_map = {
            'industry': ['IndustryAnalyst'],
            'company': ['CompanyIntelligence'],
            'geo_growth': ['GEOGrowth'],
            'analyze': ['DataAnalyst'],
        }
        names = intent_map.get(intent, list(self._agents.keys()))
        return [a for n, a in self._agents.items() if n in names]

registry = AgentRegistry()