from typing import Dict, Optional, List, Type
from agents.core.base_agent import BaseAgent


class AgentRegistry:
    _agents: Dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent):
        cls._agents[agent.agent_name] = agent

    @classmethod
    def get(cls, name: str) -> Optional[BaseAgent]:
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        return list(cls._agents.keys())

    @classmethod
    def list_all(cls) -> List[dict]:
        return [
            {"name": a.agent_name, "description": a.agent_description}
            for a in cls._agents.values()
        ]

    @classmethod
    def clear(cls):
        cls._agents = {}
