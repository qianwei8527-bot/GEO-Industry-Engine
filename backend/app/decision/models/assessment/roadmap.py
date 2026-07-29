from typing import Any, Dict, List
from app.decision.models.assessment.base import BaseAssessment
from app.context.schemas.context_schema import CompanyContext


class RoadmapEngine(BaseAssessment):
    async def calculate(self, ctx: CompanyContext) -> Dict[str, Any]:
        evidence_count = len(ctx.evidence)
        is_verified = ctx.company.is_verified
        relationship_count = len(ctx.relationships)
        geo_score = ctx.scoring.geo_score or 0

        stages = []
        if evidence_count < 5 or geo_score < 60:
            stages.append({
                "period": "0-6个月",
                "focus": "完善AI可见度，建立知识资产",
                "actions": [
                    "补充企业信息和能力描述",
                    "创建行业相关内容和案例",
                    "提交第三方可信证据"
                ]
            })

        if not is_verified or evidence_count < 8:
            stages.append({
                "period": "6-18个月",
                "focus": "完成行业认证，成为认证节点",
                "actions": [
                    "申请GEO认证（L1-L4）",
                    "积累能力证据和客户案例",
                    "建立行业关系网络"
                ]
            })

        if relationship_count < 5:
            stages.append({
                "period": "18-36个月",
                "focus": "进入产业合作网络",
                "actions": [
                    "扩展生态合作伙伴",
                    "参与行业活动和社区",
                    "探索跨行业合作机会"
                ]
            })

        if not stages:
            stages.append({
                "period": "0-36个月",
                "focus": "保持当前优势，探索新机会",
                "actions": ["持续监控GEO指数", "探索新市场机会"]
            })

        return {"stages": stages, "total_months": 36}
