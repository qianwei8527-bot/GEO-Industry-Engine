from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.context.schemas.context_schema import CompanyContext
from app.decision.models.assessment.health_score import HealthScore
from app.decision.models.assessment.opportunity_index import OpportunityIndex
from app.decision.models.assessment.strategy_fit import StrategyFit
from app.decision.models.assessment.risk_warning import RiskWarning
from app.decision.models.assessment.roadmap import RoadmapEngine
from app.decision.models.assessment.ecosystem_position import EcosystemPosition


class AssessmentEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def assess_company(self, ctx: CompanyContext) -> Dict[str, Any]:
        health = await HealthScore().calculate(ctx)
        opportunity = await OpportunityIndex().calculate(ctx)
        strategy_fit = await StrategyFit().calculate(ctx)
        risk = await RiskWarning().calculate(ctx)
        roadmap = await RoadmapEngine().calculate(ctx)
        position = await EcosystemPosition().calculate(ctx)

        return {
            "health_score": health,
            "opportunity_index": opportunity,
            "strategy_fit": strategy_fit,
            "risk_warning": risk,
            "roadmap": roadmap,
            "ecosystem_position": position,
        }
