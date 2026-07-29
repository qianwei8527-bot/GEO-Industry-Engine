from typing import Any, Dict
from app.decision.models.assessment.base import BaseAssessment
from app.context.schemas.context_schema import CompanyContext
from app.decision.scoring.weights import WeightsLoader



class OpportunityIndex(BaseAssessment):
    async def calculate(self, ctx: CompanyContext) -> Dict[str, Any]:
        industry_count = len(ctx.industries)
        capability_count = len(ctx.capabilities)
        relationship_count = len(ctx.relationships)
        evidence_count = len(ctx.evidence)
        geo_score = ctx.scoring.geo_score or 0

        market_growth = min(industry_count * 20 + 30, 100)
        demand_growth = min(capability_count * 5 + evidence_count * 3 + 20, 100)
        competition_pressure = min(relationship_count * 5 + 20, 100)
        base_readiness = min(geo_score * 0.8 + 10, 100)

        w = WeightsLoader.load("assessment")
        score = (
            market_growth * w.get("market_growth", 0.25) +
            demand_growth * w.get("demand_growth", 0.20) +
            base_readiness * w.get("base_readiness", 0.25) -
            competition_pressure * w.get("competition_pressure", -0.10)
        )

        if score >= 80: stage = "高速增长期"; window = "12-18个月"
        elif score >= 60: stage = "稳步发展期"; window = "18-24个月"
        elif score >= 40: stage = "市场探索期"; window = "24-36个月"
        else: stage = "已过高峰期"; window = "不建议进入"

        return {
            "score": round(score, 1),
            "stage": stage,
            "window": window,
            "dimensions": {
                "market_growth": round(market_growth, 1),
                "demand_growth": round(demand_growth, 1),
                "competition_pressure": round(competition_pressure, 1),
                "base_readiness": round(base_readiness, 1),
            }
        }
