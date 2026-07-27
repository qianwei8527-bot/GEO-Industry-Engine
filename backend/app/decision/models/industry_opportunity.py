from app.decision.models.base import DecisionModel
from app.decision.scoring.weights import WeightsLoader
from app.decision.scoring.calculator import ScoreCalculator
from app.decision.explanation.reason_generator import ReasonGenerator
from app.context.schemas.context_schema import IndustryContext


class IndustryOpportunityScore(DecisionModel):
    async def calculate(self, context: IndustryContext) -> dict:
        weights = WeightsLoader.load("industry_index")
        factors = {}
        factors["company_density"] = min(1.0, len(context.companies) * 0.1)
        factors["capability_depth"] = min(1.0, len(context.capabilities) * 0.08)
        factors["event_frequency"] = min(1.0, len(context.events) * 0.15)
        est_growth = 0.4 if len(context.events) > 3 else 0.2
        factors["growth_rate"] = est_growth
        score = ScoreCalculator.weighted_sum(factors, weights)
        explanation = ReasonGenerator.for_industry_index(score, factors)
        return {"score": score, "level": self._level(score), "factors": factors, **explanation}
