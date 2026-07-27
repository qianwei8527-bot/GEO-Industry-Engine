from abc import ABC, abstractmethod
from typing import Any


class DecisionModel(ABC):
    @abstractmethod
    async def calculate(self, context: Any) -> dict:
        pass

    def _level(self, score: float) -> str:
        if score >= 80: return "excellent"
        if score >= 60: return "good"
        if score >= 40: return "average"
        return "developing"
