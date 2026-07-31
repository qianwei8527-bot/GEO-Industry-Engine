"""GEO Universe Runtime Engine — Layer 1 Foundation.

The Runtime is the single entry point for all modules to access:
- Universe Registry (node types, relationships, views, lifecycle)
- Universe Rules (agent citation, decision validation)
- Scoring Configs (weights, thresholds, industry adjustments)
- Plugin Registry (views, agents, observations, renderers)
- AI Provider Registry (GPT, Claude, Gemini, etc.)

All UI, API, Agent, and Renderer modules go through Runtime, never hardcoding.
"""

from typing import Dict, List, Optional, Any
from functools import lru_cache

from app.universe.registry import UniverseRegistry, get_registry
from app.universe.plugin_registry import PluginRegistry, get_plugin_registry
from app.universe.ai_provider import AIProviderRegistry, get_ai_provider_registry
from app.universe.rules import RuleEngine, get_rule_engine
from app.core.config_loader import ConfigLoader, config_loader


class RuntimeEngine:
    """Single entry point for all Universe configuration and capabilities.

    Usage:
        rt = RuntimeEngine.get_instance()
        company_color = rt.registry.get_node_type_color("company")
        assessment_weights = rt.get_scoring_weights("assessment")
        rules = rt.rule_engine.get_all_rules()
    """

    _instance: Optional["RuntimeEngine"] = None

    def __init__(self):
        self.registry: UniverseRegistry = get_registry()
        self.rule_engine: RuleEngine = get_rule_engine()
        self.config_loader: ConfigLoader = config_loader

        # Plugin registries (populated by Plugin SDK)
        self._view_plugins: Dict[str, Any] = {}
        self._observation_plugins: Dict[str, Any] = {}
        self._agent_plugins: Dict[str, Any] = {}
        self._renderer_plugins: Dict[str, Any] = {}

        # AI Provider registry
        self._ai_providers: Dict[str, Any] = {}

        # Auto-wire PluginRegistry and AIProviderRegistry to Runtime
        self._wire_plugins()


    def _wire_plugins(self):
        """Auto-discover plugins from PluginRegistry and wire to Runtime."""
        try:
            plugin_reg = get_plugin_registry()
            plugin_reg.load_all()
            self._view_plugins = {
                pid: p for pid, p in plugin_reg._view_instances.items()
            }
            self._observation_plugins = {
                pid: p for pid, p in plugin_reg._observation_instances.items()
            }
            self._agent_plugins = {
                pid: p for pid, p in plugin_reg._agent_instances.items()
            }
            self._renderer_plugins = {
                pid: p for pid, p in plugin_reg._renderer_instances.items()
            }
        except Exception:
            pass

        try:
            ai_reg = get_ai_provider_registry()
            self._ai_providers = {
                pid: p for pid, p in ai_reg._providers.items()
            }
        except Exception:
            pass

    @classmethod
    def get_instance(cls) -> "RuntimeEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Registry shortcuts ----

    def get_node_meta(self, type_id: str):
        return self.registry.get_node_type(type_id)

    def get_node_color(self, type_id: str, default: str = "#94a3b8") -> str:
        return self.registry.get_node_type_color(type_id, default)

    def get_node_size(self, type_id: str, default: int = 14) -> int:
        return self.registry.get_node_type_size(type_id, default)

    def list_node_types(self):
        return self.registry.list_node_types()

    def list_views(self):
        return self.registry.list_views()

    def list_lifecycle_stages(self):
        return self.registry.list_lifecycle_stages()

    def list_relationship_types(self):
        return self.registry.list_relationship_types()

    def list_capabilities(self):
        return self.registry.list_capabilities()

    # ---- Rule shortcuts ----

    def get_rule(self, rule_id: str):
        return self.rule_engine.get_rule(rule_id)

    def get_all_rules(self):
        return self.rule_engine.get_all_rules()

    def cite_rule(self, rule_id: str, explanation: str) -> str:
        return self.rule_engine.cite(rule_id, explanation)

    def validate_decision(self, decision_type: str, factors: Dict[str, float]):
        return self.rule_engine.validate(decision_type, factors)

    # ---- Scoring configs ----

    def get_scoring_weights(self, config_name: str = "assessment") -> Dict[str, float]:
        return self.config_loader.get_all_weights(config_name)

    def get_scoring_thresholds(self, config_name: str, section: str) -> Dict[str, int]:
        return self.config_loader.get_thresholds(config_name, section)

    def get_scoring_config(self, config_name: str) -> Dict[str, Any]:
        return self.config_loader.get_scoring_config(config_name)

    def reload_scoring(self, name: Optional[str] = None):
        self.config_loader.reload(name)

    # ---- Plugin management ----

    def register_view_plugin(self, view_id: str, plugin: Any):
        self._view_plugins[view_id] = plugin

    def get_view_plugin(self, view_id: str) -> Optional[Any]:
        return self._view_plugins.get(view_id)

    def list_view_plugins(self) -> Dict[str, Any]:
        return dict(self._view_plugins)

    def register_agent_plugin(self, agent_id: str, plugin: Any):
        self._agent_plugins[agent_id] = plugin

    def get_agent_plugin(self, agent_id: str) -> Optional[Any]:
        return self._agent_plugins.get(agent_id)

    def register_observation_plugin(self, obs_id: str, plugin: Any):
        self._observation_plugins[obs_id] = plugin

    def register_renderer_plugin(self, renderer_id: str, plugin: Any):
        self._renderer_plugins[renderer_id] = plugin

    # ---- AI Provider management ----

    def register_ai_provider(self, provider_id: str, provider: Any):
        self._ai_providers[provider_id] = provider

    def get_ai_provider(self, provider_id: str) -> Optional[Any]:
        return self._ai_providers.get(provider_id)

    def list_ai_providers(self) -> List[str]:
        return list(self._ai_providers.keys())

    # ---- Full export ----

    def export_full(self) -> Dict[str, Any]:
        """Export complete Runtime state for frontend consumption."""
        return {
            "registry": self.registry.export_full(),
            "rules": {
                "count": len(self.rule_engine.get_all_rules()),
                "categories": self.rule_engine.get_categories(),
            },
            "scoring": {
                "available": self.config_loader.list_available(),
            },
            "plugins": {
                "views": list(self._view_plugins.keys()),
                "agents": list(self._agent_plugins.keys()),
                "observations": list(self._observation_plugins.keys()),
                "renderers": list(self._renderer_plugins.keys()),
                "ai_providers": list(self._ai_providers.keys()),
            },
        }


@lru_cache()
def get_runtime() -> RuntimeEngine:
    return RuntimeEngine.get_instance()
