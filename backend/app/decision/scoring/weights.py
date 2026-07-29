"""YAML驱动的评分配置加载器 — v2.0 支持嵌套结构和行业系数"""
import os
import yaml
from typing import Any, Optional
from functools import lru_cache

CONFIG_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "config", "scoring")


class WeightsLoader:
    """从 config/scoring/*.yaml 加载评分权重、阈值和行业调整系数"""
    _cache: dict[str, dict] = {}

    @classmethod
    def _resolve_path(cls, name: str) -> str:
        """解析配置文件名"""
        if not name.endswith(".yaml"):
            name = f"{name}.yaml"
        return os.path.join(CONFIG_ROOT, name)

    @classmethod
    def load(cls, name: str) -> dict:
        """加载完整的YAML配置（含weights/thresholds/sub_weights/industry_adjustments）"""
        if name in cls._cache:
            return cls._cache[name]
        path = cls._resolve_path(name)
        if not os.path.exists(path):
            cls._cache[name] = {}
            return {}
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        cls._cache[name] = config or {}
        return cls._cache[name]

    @classmethod
    def get_weights(cls, name: str, section: Optional[str] = None) -> dict[str, float]:
        """获取权重字典
        Args:
            name: 配置文件名（不含.yaml）
            section: 二级权重key（如 'identity_position', 'opportunity_discovery'）
                     不指定则返回顶层 weights
        """
        config = cls.load(name)
        weights = config.get("weights", {})
        if section and section in config:
            weights = config[section].get("weights", weights)
        return {k: float(v) for k, v in weights.items() if isinstance(v, (int, float))}

    @classmethod
    def get_sub_weights(cls, name: str, dimension: str) -> dict[str, float]:
        """获取二级维度权重"""
        config = cls.load(name)
        section = config.get(dimension, {})
        return {k: float(v) for k, v in section.get("sub_weights", {}).items()
                if isinstance(v, (int, float))}

    @classmethod
    def get_thresholds(cls, name: str, section: Optional[str] = None) -> dict[str, float]:
        """获取阈值"""
        config = cls.load(name)
        thresholds = config.get("thresholds", {})
        if section and section in config:
            thresholds = config[section].get("thresholds", thresholds)
        return {k: float(v) for k, v in thresholds.items() if isinstance(v, (int, float))}

    @classmethod
    def get_industry_adjustments(cls, name: str) -> dict[str, Any]:
        """获取行业调整系数"""
        config = cls.load(name)
        return config.get("industry_adjustments", {})

    @classmethod
    def get_computation_config(cls, name: str) -> dict:
        """获取计算配置（batch_size, cache_ttl等）"""
        config = cls.load(name)
        return config.get("computation", {})

    @classmethod
    def clear_cache(cls):
        """清除缓存（用于配置热加载）"""
        cls._cache.clear()


# 便捷的单例函数
def load_weights(name: str, section: Optional[str] = None) -> dict[str, float]:
    return WeightsLoader.get_weights(name, section)

def load_thresholds(name: str, section: Optional[str] = None) -> dict[str, float]:
    return WeightsLoader.get_thresholds(name, section)

def load_industry_coefficients(name: str) -> dict[str, Any]:
    return WeightsLoader.get_industry_adjustments(name)