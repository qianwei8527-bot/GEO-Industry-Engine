"""评分计算器 — 集成YAML配置的决策计算"""
from typing import Optional
from app.decision.scoring.weights import WeightsLoader


class ScoreCalculator:
    """基于YAML配置的评分计算器，支持多层嵌套权重和行业系数调整"""

    @staticmethod
    def weighted_sum(factors: dict[str, float], weights: dict[str, float]) -> float:
        """加权求和：sum(factor_i * weight_i) / sum(weights) * 100"""
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        weighted = sum(factors.get(k, 0) * v for k, v in weights.items())
        return round(min(100.0, weighted / total_weight * 100), 1)

    @staticmethod
    def normalize(value: float, min_val: float, max_val: float) -> float:
        """Min-Max归一化到0-100"""
        if max_val <= min_val:
            return 50.0
        return round((value - min_val) / (max_val - min_val) * 100, 1)

    @staticmethod
    def level(score: float, thresholds: dict[str, float]) -> str:
        """根据阈值判定等级"""
        high = thresholds.get("high", 80)
        medium = thresholds.get("medium", 50)
        low = thresholds.get("low", 30)
        if score >= high:
            return "excellent"
        if score >= medium:
            return "good"
        if score >= low:
            return "average"
        return "developing"

    # === YAML驱动的便捷方法 ===

    @classmethod
    def score_from_yaml(cls, config_name: str, factors: dict[str, float],
                        section: Optional[str] = None) -> dict:
        """从YAML配置计算评分，返回 score + level + reason"""
        weights = WeightsLoader.get_weights(config_name, section)
        thresholds = WeightsLoader.get_thresholds(config_name, section)
        score = cls.weighted_sum(factors, weights)
        return {
            "score": score,
            "level": cls.level(score, thresholds),
            "weights_used": weights,
        }

    @classmethod
    def apply_industry_adjustment(cls, config_name: str, industry: str,
                                   scores: dict[str, float]) -> dict[str, float]:
        """应用行业系数调整"""
        adjustments = WeightsLoader.get_industry_adjustments(config_name)
        if industry not in adjustments:
            return scores
        adj = adjustments[industry]
        adjusted = dict(scores)
        for key, multiplier in adj.items():
            if key.endswith("_multiplier") and key.replace("_multiplier", "") in adjusted:
                dim = key.replace("_multiplier", "")
                adjusted[dim] = round(min(100.0, adjusted[dim] * multiplier), 1)
            elif key.endswith("_add") and key.replace("_add", "") in adjusted:
                dim = key.replace("_add", "")
                adjusted[dim] = round(min(100.0, adjusted[dim] + multiplier), 1)
        return adjusted

    @classmethod
    def get_computation_config(cls, config_name: str) -> dict:
        """获取计算配置（batch_size, cache_ttl等）"""
        return WeightsLoader.get_computation_config(config_name)