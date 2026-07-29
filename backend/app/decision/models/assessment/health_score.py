from typing import Any, Dict
from app.decision.models.assessment.base import BaseAssessment
from app.context.schemas.context_schema import CompanyContext
from app.decision.scoring.weights import WeightsLoader



class HealthScore(BaseAssessment):
    async def calculate(self, ctx: CompanyContext) -> Dict[str, Any]:
        visibility = ctx.scoring.geo_score or 0
        evidence_count = len(ctx.evidence)
        relationship_types = len(set(r.relation_type for r in ctx.relationships))
        trust = ctx.scoring.trust_score or 0
        capability = ctx.scoring.capability_match or 0

        evidence_score = min(evidence_count / 10, 1.0) * 100
        relationship_score = min(relationship_types / 5, 1.0) * 100

        w = WeightsLoader.load("assessment")
        score = (
            visibility * w.get("visibility_weight", 0.25) +
            evidence_score * w.get("evidence_weight", 0.20) +
            relationship_score * w.get("relationship_weight", 0.10) +
            trust * 100 * w.get("trust_weight", 0.15) +
            capability * 100 * w.get("capability_weight", 0.10)
        )

        level = "S" if score >= 85 else "A" if score >= 70 else "B" if score >= 55 else "C"

        strengths = []
        weaknesses = []
        if visibility >= 70: strengths.append("AI可见度较高")
        else: weaknesses.append("AI可见度不足")
        if evidence_count >= 5: strengths.append("数字资产丰富")
        else: weaknesses.append("数字资产不足")
        if relationship_types >= 3: strengths.append("生态关系广泛")
        else: weaknesses.append("生态关系有限")
        if ctx.company.is_verified: strengths.append("已通过认证")
        else: weaknesses.append("尚未认证")

        return {
            "score": round(score, 1),
            "level": level,
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "dimensions": {
                "visibility": round(visibility, 1),
                "evidence_completeness": round(evidence_score, 1),
                "relationship_diversity": round(relationship_score, 1),
                "trust": round(trust * 100, 1),
                "capability_match": round(capability * 100, 1),
            }
        }
