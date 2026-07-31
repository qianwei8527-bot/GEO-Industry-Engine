# GEO Universe Module
# Layer 0: Rule Engine + Registry
# Layer 1: Runtime Engine (unified entry point)
# Layer 2: Plugin SDK (extensible views, observations, agents, renderers)
# Layer 3: AI Provider Interface (unified model adapters)

from app.universe.rules import RuleEngine, UniverseRules, get_rule_engine
from app.universe.world_model import LivingWorldModel, KnowledgeCandidate, get_world_model
from app.universe.position_engine import PositionEngine, PositionReport, get_position_engine
from app.universe.memory_engine import MemoryEngine, Fact, Evidence, MemoryEvent, Story, get_memory_engine
from app.universe.capability_engine import CapabilityRegistry, Capability, get_capability_registry, UNIVERSAL_CAPABILITIES
from app.universe.context_engine import ContextEngine, NodeContext, get_context_engine
from app.universe.decision_engine import DecisionEngine, CandidatePath, DecisionReport, get_decision_engine
from app.universe.possibility_engine import PossibilityEngine, PossibilityGraph, DecisionMemory, get_possibility_engine
from app.universe.future_registry import FutureStateRegistry, FutureStateTemplate, get_future_registry
from app.universe.node import UniverseNode, NodePosition, NodeTrajectory, is_valid_node_type, get_node_type_label, get_node_type_color
from app.universe.registry import UniverseRegistry, get_registry
from app.universe.runtime import RuntimeEngine, get_runtime
from app.universe.plugin import (
    ViewPlugin, ObservationPlugin, AgentPlugin, RendererPlugin,
    PluginMeta, ObservationResult, AgentResult,
)
from app.universe.plugin_registry import PluginRegistry, get_plugin_registry
from app.universe.ai_provider import (
    BaseAIProvider, AIProviderRegistry, get_ai_provider_registry,
    ChatMessage, ChatCompletionRequest, ChatCompletionResponse,
    OpenAIProvider, ClaudeProvider, GeminiProvider, DeepSeekProvider,
)

__all__ = [
    # Layer 0
    "RuleEngine", "UniverseRules", "get_rule_engine",
    "UniverseRegistry", "get_registry",
    "UniverseNode", "NodePosition", "NodeTrajectory", "is_valid_node_type", "get_node_type_label", "get_node_type_color",
    # Layer 1
    "RuntimeEngine", "get_runtime",
    # Layer 2
    "ViewPlugin", "ObservationPlugin", "AgentPlugin", "RendererPlugin",
    "PluginMeta", "ObservationResult", "AgentResult",
    "PluginRegistry", "get_plugin_registry",
    # Layer 3
    "BaseAIProvider", "AIProviderRegistry", "get_ai_provider_registry",
    "ChatMessage", "ChatCompletionRequest", "ChatCompletionResponse",
    "OpenAIProvider", "ClaudeProvider", "GeminiProvider", "DeepSeekProvider",
    "LivingWorldModel", "KnowledgeCandidate", "get_world_model",
    "PositionEngine", "PositionReport", "get_position_engine",
    "MemoryEngine", "Fact", "Evidence", "MemoryEvent", "Story", "get_memory_engine",
    "CapabilityRegistry", "Capability", "get_capability_registry", "UNIVERSAL_CAPABILITIES",
    "ContextEngine", "NodeContext", "get_context_engine",
    "DecisionEngine", "CandidatePath", "DecisionReport", "get_decision_engine",
    "PossibilityEngine", "PossibilityGraph", "DecisionMemory", "get_possibility_engine",
    "FutureStateRegistry", "FutureStateTemplate", "get_future_registry",
]
