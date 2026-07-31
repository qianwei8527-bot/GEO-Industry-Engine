# GEO Universe Plugin SDK
# Defines base interfaces for all pluggable components:
# - ViewPlugin: custom rendering filters for each Universe View
# - ObservationPlugin: data collectors that feed Observation Engine
# - AgentPlugin: agent implementations
# - RendererPlugin: graph/layout renderers (2D, 3D, etc.)

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class PluginMeta:
    """Metadata for a registered plugin."""
    plugin_id: str
    name: str
    version: str
    author: str = ""
    description: str = ""
    category: str = ""
    config_schema: Dict[str, Any] = field(default_factory=dict)
    defaults: Dict[str, Any] = field(default_factory=dict)


# ---- View Plugin Interface ----

class ViewPlugin(ABC):
    """A ViewPlugin applies filtering/transformation to graph data
    based on the user current view perspective.
    """
    meta: PluginMeta

    @abstractmethod
    def filter_nodes(self, nodes: List[Dict], params: Dict[str, Any]) -> List[Dict]:
        """Filter which nodes are visible in this view."""
        ...

    @abstractmethod
    def filter_edges(self, edges: List[Dict], params: Dict[str, Any]) -> List[Dict]:
        """Filter which edges are visible in this view."""
        ...

    @abstractmethod
    def transform_node_style(self, node: Dict, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return style overrides for a node (size, color, highlight)."""
        ...

    def get_layout(self) -> str:
        return "cose"


# ---- Observation Plugin Interface ----

@dataclass
class ObservationResult:
    source: str
    signals: List[Dict[str, Any]]
    candidate_changes: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ObservationPlugin(ABC):
    """An ObservationPlugin scans external or internal sources
    and produces signals + candidate changes for the World Engine.
    """
    meta: PluginMeta

    @abstractmethod
    async def observe(self, params: Dict[str, Any]) -> ObservationResult:
        """Run observation and return structured results."""
        ...

    def validate_source(self, source_uri: str) -> bool:
        return True


# ---- Agent Plugin Interface ----

@dataclass
class AgentResult:
    agent_id: str
    report: str
    data: Dict[str, Any]
    citations: List[str] = field(default_factory=list)
    confidence: float = 0.0


class AgentPlugin(ABC):
    """An AgentPlugin implements a specific analysis/diagnosis/matching task."""
    meta: PluginMeta

    @abstractmethod
    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResult:
        """Execute the agent task."""
        ...

    def get_capabilities(self) -> List[str]:
        return []


# ---- Renderer Plugin Interface ----

class RendererPlugin(ABC):
    """A RendererPlugin handles graph layout and rendering for a specific mode."""
    meta: PluginMeta

    @abstractmethod
    def compute_layout(self, nodes: List[Dict], edges: List[Dict], params: Dict[str, Any]) -> Dict[str, Any]:
        """Compute positions for all nodes. Returns {node_id: {x, y, z?}}."""
        ...

    def get_supported_formats(self) -> List[str]:
        return ["2d-canvas"]

    def render(self, nodes: List[Dict], edges: List[Dict], params: Dict[str, Any]) -> Any:
        return None
