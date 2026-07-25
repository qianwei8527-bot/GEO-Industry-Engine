from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """所有Agent的基类"""
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass

class AgentRegistry:
    """Agent注册中心"""
    _agents: Dict[str, BaseAgent] = {}
    
    @classmethod
    def register(cls, agent: BaseAgent):
        cls._agents[agent.name] = agent
    
    @classmethod
    def get(cls, name: str) -> BaseAgent | None:
        return cls._agents.get(name)
    
    @classmethod
    def list_agents(cls) -> list[str]:
        return list(cls._agents.keys())
