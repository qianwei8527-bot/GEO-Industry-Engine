from typing import Any, Dict
from app.decision.models.assessment.base import BaseAssessment
from app.context.schemas.context_schema import CompanyContext


class EcosystemPosition(BaseAssessment):
    async def calculate(self, ctx: CompanyContext) -> Dict[str, Any]:
        industry_count = len(ctx.industries)
        capability_count = len(ctx.capabilities)
        relationship_types = len(set(r.relation_type for r in ctx.relationships))
        is_verified = ctx.company.is_verified
        geo_score = ctx.scoring.geo_score or 0

        if is_verified and geo_score >= 75: level = "L4"
        elif is_verified and capability_count >= 3: level = "L3"
        elif is_verified: level = "L2"
        else: level = "L1"

        level_names = {"L1": "身份认证", "L2": "能力认证",
                       "L3": "行业认证", "L4": "平台贡献"}

        if industry_count >= 2:
            position_type = "跨行业服务商"
        elif capability_count >= 3:
            position_type = "专业能力提供商"
        elif capability_count >= 1:
            position_type = "单项服务提供商"
        else:
            position_type = "新入市场参与者"

        if relationship_types >= 4: next_step = "优先袔合质量而非数量"
        elif is_verified: next_step = "扩展生态关系网络"
        else: next_step = "建议先完成L1身份认证"

        return {
            "current_position": position_type,
            "current_level": level,
            "level_name": level_names.get(level, ""),
            "next_step": next_step,
            "dimensions": {
                "industry_coverage": min(industry_count * 25, 100),
                "capability_depth": min(capability_count * 20, 100),
                "relationship_breadth": min(relationship_types * 20, 100),
                "certification_level": 25 if is_verified else 0,
            }
        }
