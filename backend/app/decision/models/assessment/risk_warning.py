from typing import Any, Dict
from app.decision.models.assessment.base import BaseAssessment
from app.context.schemas.context_schema import CompanyContext
from app.decision.scoring.weights import WeightsLoader



class RiskWarning(BaseAssessment):
    async def calculate(self, ctx: CompanyContext) -> Dict[str, Any]:
        capabilities = ctx.capabilities
        relationships = ctx.relationships
        evidence = ctx.evidence
        geo_score = ctx.scoring.geo_score or 0
        trust_score = ctx.scoring.trust_score or 0

        competition_risk = 100 - min(len(relationships) * 10, 80)
        tech_risk = 100 - min(len(capabilities) * 8, 70)
        brand_risk = 100 - min(geo_score * 0.7, 70)
        trust_risk = 100 - (trust_score * 100)
        evidence_risk = 100 - min(len(evidence) * 15, 90)

        total_risks = [
            ("市场竞争", competition_risk),
            ("技术替代", tech_risk),
            ("品牌知名度", brand_risk),
            ("信任认可", trust_risk),
            ("数据资产", evidence_risk),
        ]

        overall = round(sum(r for _, r in total_risks) / len(total_risks), 1)
        if overall >= 70: level = "红色（高风险）"
        elif overall >= 45: level = "黄色（中等风险）"
        else: level = "绿色（低风险）"

        main_risks = sorted(total_risks, key=lambda x: x[1], reverse=True)[:3]

        return {
            "overall_risk": overall,
            "level": level,
            "main_risks": [{"name": n, "score": round(s, 1)} for n, s in main_risks],
        }
