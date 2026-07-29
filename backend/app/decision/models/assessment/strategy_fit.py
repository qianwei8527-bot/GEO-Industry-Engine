from typing import Any, Dict
from app.decision.models.assessment.base import BaseAssessment
from app.context.schemas.context_schema import CompanyContext
from app.decision.scoring.weights import WeightsLoader



class StrategyFit(BaseAssessment):
    async def calculate(self, ctx: CompanyContext) -> Dict[str, Any]:
        capabilities = ctx.capabilities
        relationships = ctx.relationships
        is_verified = ctx.company.is_verified

        tech = min(len([c for c in capabilities if c.level >= 2]) * 20 + 30, 100)
        talent = min(len(capabilities) * 10 + 20, 100)
        channel = min(len(relationships) * 10 + 20, 100)
        industry_exp = len(ctx.industries) * 20 + 20
        funding = 100 if is_verified else 60

        w = WeightsLoader.load("assessment")
        score = (
            tech * w.get("tech_weight", 0.20) +
            talent * w.get("talent_weight", 0.15) +
            channel * w.get("channel_weight", 0.20) +
            min(industry_exp, 100) * w.get("experience_weight", 0.25) +
            funding * w.get("funding_weight", 0.20)
        )

        if score >= 75: suggestion = "建议自主进入"
        elif score >= 50: suggestion = "建议生态合作切入"
        else: suggestion = "不建议直接进入，优先补齐能力"

        return {
            "score": round(score, 1),
            "suggestion": suggestion,
            "dimensions": {
                "tech_capability": round(tech, 1),
                "talent_capability": round(talent, 1),
                "channel_resource": round(channel, 1),
                "industry_experience": round(min(industry_exp, 100), 1),
                "funding_capability": round(funding, 1),
            }
        }
