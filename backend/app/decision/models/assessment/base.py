from abc import ABC, abstractmethod
from typing import Any, Dict
from app.context.schemas.context_schema import CompanyContext


class BaseAssessment(ABC):
    @abstractmethod
    async def calculate(self, ctx: CompanyContext) -> Dict[str, Any]:
        pass
