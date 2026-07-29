"""
GEO-Industry-Engine Decision Engine
P0-C.3-1: YAML接入 — 所有评分权重从 config/scoring/*.yaml 读取，不再硬编码。
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.context.engine import ContextEngine
from app.context.schemas.context_schema import CompanyContext, IndustryContext
from app.decision.models.geo_visibility import GEOVisibilityScore
from app.decision.models.industry_opportunity import IndustryOpportunityScore
from app.decision.models.company_growth import (
    CompanyGrowthScore, CompetitivePosition, GEORoadmap,
    ContentStrategy, MarketConnection,
)
from app.decision.models.capability_match import CapabilityMatchScore
from app.decision.models.assessment.engine import AssessmentEngine
from app.decision.recommendation.recommendation_engine import RecommendationEngine
from app.core.config_loader import config_loader


class DecisionEngine:
    """
    GEO产业中央决策引擎。
    所有评分/评估/预测/推荐能力的中枢入口。

    权重来源: config/scoring/*.yaml (由 ConfigLoader 加载)
    禁止硬编码权重。
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.context = ContextEngine(db)
        self._load_weights()

    def _load_weights(self):
        """从YAML加载权重，引擎实例化时调用一次。"""
        self.weights = config_loader.get_all_weights("assessment")
        self.thresholds = {
            "identity": config_loader.get_thresholds("assessment", "identity_position"),
            "opportunity": config_loader.get_thresholds("assessment", "opportunity_discovery"),
            "risk": config_loader.get_thresholds("assessment", "risk_warning"),
        }
        self.industry_adjustments = config_loader.get_industry_adjustments("assessment")
        self.computation = config_loader.get_computation_config("assessment")

    def reload_weights(self):
        """热重载YAML配置，无需重启进程。管理后台可调用。"""
        config_loader.reload("assessment")
        self._load_weights()

    def get_weight(self, key: str, default: float = 0.5) -> float:
        """获取单个权重值，YAML未定义时回退到默认值。"""
        return self.weights.get(key, default)

    def get_threshold_level(self, category: str, score: float) -> str:
        """根据评分返回阈值等级标签。"""
        thresholds = self.thresholds.get(category, {})
        for level, min_score in sorted(thresholds.items(), key=lambda x: -x[1]):
            if score >= min_score:
                return level
        return "unknown"

    async def analyze_company(self, company_id: str) -> dict:
        ctx = await self.context.get_company_context(company_id)
        scores = {}
        scores["visibility"] = await GEOVisibilityScore().calculate(ctx)
        scores["company_growth"] = await CompanyGrowthScore().calculate(ctx)
        scores["competitive_position"] = await CompetitivePosition().calculate(ctx)
        scores["roadmap"] = await GEORoadmap().calculate(ctx)
        scores["content_strategy"] = await ContentStrategy().calculate(ctx)
        scores["market_connection"] = await MarketConnection().calculate(ctx)
        recommendations = await RecommendationEngine.generate(ctx, scores)
        return {
            "company_id": company_id,
            "company_name": ctx.company.name,
            "scores": scores,
            "overall": round(sum(s["score"] for s in scores.values()) / len(scores), 1),
            "recommendations": recommendations,
            "weights_source": "config/scoring/assessment.yaml",
        }

    async def analyze_industry(self, industry_id: str) -> dict:
        ctx = await self.context.get_industry_context(industry_id)
        score = await IndustryOpportunityScore().calculate(ctx)
        return {
            "industry_id": industry_id,
            "industry_name": ctx.industry.name,
            "scores": {"industry_index": score},
            "company_count": len(ctx.companies),
            "capability_count": len(ctx.capabilities),
        }

    async def analyze(self, query_text: str, limit: int = 10) -> dict:
        result = await self.context.query(query_text, limit)
        return {"query": query_text, "results": result.dict()}

    async def assess_company(self, company_id: str) -> dict:
        ctx = await self.context.get_company_context(company_id)
        return await AssessmentEngine(self.db).assess_company(ctx)
