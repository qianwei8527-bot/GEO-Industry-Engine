"""Universe Rule Engine - Layer 0 Foundation."""

import os, yaml
from typing import Dict, List, Optional, Any
from functools import lru_cache

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_RULES_PATH = os.path.join(_PROJECT_ROOT, "config", "universe", "rules.yaml")

class UniverseRules:
    def __init__(self, config_path: str = _RULES_PATH):
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        self.version = raw.get("version", "unknown")
        self.description = raw.get("description", "")
        self.rules = raw.get("rules", [])
        self.categories = raw.get("categories", {})
        self.citation_protocol = raw.get("agent_citation_protocol", {})
        self.map_triggers = raw.get("map_update_triggers", {})
        self._by_id = {r["id"]: r for r in self.rules}
        self._by_category: Dict[str, List[Dict]] = {}
        for r in self.rules:
            self._by_category.setdefault(r.get("category", "general"), []).append(r)

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        return self._by_id.get(rule_id)
    def get_rules_by_category(self, category: str) -> List[Dict[str, Any]]:
        return self._by_category.get(category, [])
    def get_rules_affecting_layer(self, layer: str) -> List[Dict[str, Any]]:
        return [r for r in self.rules if layer in r.get("affects_layers", [])]
    def get_rules_triggered_by(self, trigger: str) -> List[Dict[str, Any]]:
        return [r for r in self.rules if trigger in r.get("triggers", [])]
    def format_citation(self, rule_id: str, explanation: str) -> str:
        rule = self.get_rule(rule_id)
        if not rule:
            return f"Rule {rule_id}: {explanation}"
        return f"Rule {rule_id}: {rule['name']} -> {explanation}"
    def get_all_ids(self) -> List[str]:
        return list(self._by_id.keys())
    def validate_decision(self, decision_type: str, factors: Dict[str, float]) -> Dict[str, Any]:
        applicable = self.get_rules_by_category(decision_type)
        return {"decision_type": decision_type, "applicable_rules": [r["id"] for r in applicable],
                "factors": factors, "valid": len(applicable) > 0,
                "warnings": [] if applicable else [f"No rules found for {decision_type}"]}

class RuleEngine:
    _instance: Optional["RuleEngine"] = None
    def __init__(self):
        self.rules = UniverseRules()
    @classmethod
    def get_instance(cls) -> "RuleEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    def cite(self, rule_id: str, explanation: str) -> str:
        return self.rules.format_citation(rule_id, explanation)
    def validate(self, decision_type: str, factors: Dict[str, float]) -> Dict[str, Any]:
        return self.rules.validate_decision(decision_type, factors)
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        return self.rules.get_rule(rule_id)
    def get_all_rules(self) -> List[Dict[str, Any]]:
        return self.rules.rules
    def get_categories(self) -> Dict[str, List[str]]:
        return self.rules.categories
    def get_citation_protocol(self) -> Dict[str, Any]:
        return self.rules.citation_protocol
    def get_triggers_for_event(self, event_type: str) -> List[Dict[str, str]]:
        return self.rules.map_triggers.get(f"on_{event_type}", [])

@lru_cache()
def get_rule_engine() -> RuleEngine:
    return RuleEngine.get_instance()
