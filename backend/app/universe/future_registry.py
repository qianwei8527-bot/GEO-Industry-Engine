# GEO Universe Future State Registry
# Phase C3.5: Future states as first-class Universe-managed assets.
# All future evolution paths are configurable, not hardcoded.
# Cross-industry templates enable reuse: education, medical, legal, etc.

import os
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from functools import lru_cache

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_FUTURES_PATH = os.path.join(_PROJECT_ROOT, "config", "universe", "futures.yaml")


@dataclass
class FutureStateTemplate:
    id: str
    label: str
    label_en: str
    order: int
    stage: str
    description: str
    required_capabilities: List[str] = field(default_factory=list)
    min_evidence: int = 0
    min_relationships: int = 0
    min_influence: float = 0.0
    reputation_min: str = ""
    success_conditions: List[str] = field(default_factory=list)
    failure_conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "label_en": self.label_en,
            "order": self.order,
            "stage": self.stage,
            "description": self.description,
            "required_capabilities": self.required_capabilities,
            "min_evidence": self.min_evidence,
            "min_relationships": self.min_relationships,
            "min_influence": self.min_influence,
            "reputation_min": self.reputation_min,
            "success_conditions": self.success_conditions,
            "failure_conditions": self.failure_conditions,
        }


class FutureStateRegistry:
    _instance = None

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = _FUTURES_PATH
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        self.version = raw.get("version", "unknown")
        self.description = raw.get("description", "")

        self._company_futures = self._parse(raw.get("company_futures", []))
        self._provider_futures = self._parse(raw.get("provider_futures", []))
        self._ai_agent_futures = self._parse(raw.get("ai_agent_futures", []))
        self._cross_industry = raw.get("cross_industry", {})

    def _parse(self, items: List[Dict]) -> List[FutureStateTemplate]:
        return [FutureStateTemplate(**item) for item in items]

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def get_for_node_type(self, node_type: str) -> List[FutureStateTemplate]:
        key = f"_{node_type}_futures"
        return getattr(self, key, [])

    def get_reachable(self, node_type: str, current_stage: str,
                      capability_count: int, evidence_count: int,
                      relationship_count: int, influence: float,
                      reputation: str) -> List[FutureStateTemplate]:
        futures = self.get_for_node_type(node_type)
        if not futures:
            return []

        rep_rank = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "N/A": 0}
        reachable = []
        for f in futures:
            if f.stage == current_stage:
                continue
            meets_caps = capability_count >= len(f.required_capabilities)
            meets_ev = evidence_count >= f.min_evidence
            meets_rel = relationship_count >= f.min_relationships
            meets_inf = influence >= f.min_influence
            meets_rep = (not f.reputation_min or
                         rep_rank.get(reputation, 0) >= rep_rank.get(f.reputation_min, 0))
            if meets_caps and meets_ev and meets_rel and meets_inf and meets_rep:
                reachable.append(f)
        return sorted(reachable, key=lambda x: x.order)

    def get_next(self, node_type: str, current_stage: str,
                 **kwargs) -> Optional[FutureStateTemplate]:
        reachable = self.get_reachable(node_type, current_stage, **kwargs)
        return reachable[0] if reachable else None

    def get_all_templates(self) -> Dict[str, List[Dict]]:
        return {
            "company": [f.to_dict() for f in self._company_futures],
            "provider": [f.to_dict() for f in self._provider_futures],
            "ai_agent": [f.to_dict() for f in self._ai_agent_futures],
            "cross_industry": self._cross_industry,
        }

    def get_cross_industry_template(self, industry: str) -> Optional[Dict]:
        return self._cross_industry.get(industry)

    def export_full(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "description": self.description,
            "templates": self.get_all_templates(),
        }


@lru_cache()
def get_future_registry() -> FutureStateRegistry:
    return FutureStateRegistry.get_instance()
