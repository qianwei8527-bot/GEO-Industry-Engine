"""
GEO-Industry-Engine YAML Config Loader
Sprint 0.5 / P0-C.3-1: YAML接入Decision Engine

加载 config/scoring/*.yaml 到 Decision Engine、Context Engine、Agent OS。
支持配置生命周期: active / experiments / deprecated。
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone


class ConfigLoader:
    """Loads and caches YAML scoring configurations with lifecycle management."""

    _instance: Optional["ConfigLoader"] = None
    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, config_root: str = None):
        if config_root is None:
            # Auto-detect project root (4 levels up: core -> app -> backend -> project_root)
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            self.config_root = project_root / "config"
        else:
            self.config_root = Path(config_root)
        self._loaded_at: Dict[str, datetime] = {}

    @classmethod
    def singleton(cls, config_root: str = None) -> "ConfigLoader":
        if cls._instance is None:
            cls._instance = cls(config_root)
        return cls._instance

    # ---- Public API ----

    def get_scoring_config(self, name: str) -> Dict[str, Any]:
        """Load a scoring YAML by name (e.g. 'assessment', 'geo_visibility')."""
        cache_key = f"scoring.{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        data = self._load_yaml(f"scoring/{name}.yaml")
        self._cache[cache_key] = data
        self._loaded_at[cache_key] = datetime.now(timezone.utc)
        return data

    def get_all_weights(self, config_name: str = "assessment") -> Dict[str, float]:
        """Extract flat weight map from a scoring config."""
        cfg = self.get_scoring_config(config_name)
        weights = {}

        for section in ["identity_position", "opportunity_discovery", "risk_warning"]:
            if section in cfg and "weights" in cfg[section]:
                for k, v in cfg[section]["weights"].items():
                    weights[k] = float(v)

        if "strategic_roadmap" in cfg and "phase_weights" in cfg["strategic_roadmap"]:
            for k, v in cfg["strategic_roadmap"]["phase_weights"].items():
                weights[k] = float(v)

        return weights

    def get_thresholds(self, config_name: str, section: str) -> Dict[str, int]:
        """Get thresholds for a specific section."""
        cfg = self.get_scoring_config(config_name)
        return cfg.get(section, {}).get("thresholds", {})

    def get_industry_adjustments(self, config_name: str = "assessment") -> Dict[str, Any]:
        """Get industry adjustment multipliers."""
        cfg = self.get_scoring_config(config_name)
        return cfg.get("industry_adjustments", {})

    def get_computation_config(self, config_name: str = "assessment") -> Dict[str, Any]:
        """Get computation parameters (batch_size, cache_ttl, etc.)."""
        cfg = self.get_scoring_config(config_name)
        return cfg.get("computation", {})

    def reload(self, name: Optional[str] = None):
        """Invalidate cache for one or all configs."""
        if name:
            self._cache.pop(f"scoring.{name}", None)
        else:
            self._cache.clear()

    def list_available(self) -> list:
        """List all available scoring config names."""
        scoring_dir = self.config_root / "scoring"
        if not scoring_dir.exists():
            return []
        return sorted([
            p.stem for p in scoring_dir.glob("*.yaml")
            if not p.name.startswith("_")
        ])

    def validate(self, name: str) -> Dict[str, Any]:
        """Validate a scoring config has required sections."""
        cfg = self.get_scoring_config(name)
        report = {"config": name, "valid": True, "issues": []}
        required_sections = ["identity_position", "opportunity_discovery", "risk_warning", "strategic_roadmap"]
        for section in required_sections:
            if section not in cfg:
                report["valid"] = False
                report["issues"].append(f"Missing section: {section}")
            elif "weights" not in cfg.get(section, {}):
                report["issues"].append(f"Section {section} missing weights")
        return report

    # ---- Internal ----

    def _load_yaml(self, relative_path: str) -> Dict[str, Any]:
        full_path = self.config_root / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"Config not found: {full_path}")
        with open(full_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict in {full_path}, got {type(data)}")
        return data


# Singleton accessor
config_loader = ConfigLoader.singleton()



