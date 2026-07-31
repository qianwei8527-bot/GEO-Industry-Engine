# GEO Universe Node ? Unified base for all node types.
# Every node in the Universe inherits from this class.
# A node is NOT a SQL row. It is a living Universe Object with:
#   Identity, Memory, Observation, Knowledge, Relationship, Position, Trajectory, Capability

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid

from app.universe.registry import UniverseRegistry, get_registry


# ---- Position: where the node stands in the Universe ----

@dataclass
class NodePosition:
    """Multi-dimensional position of a node in the Universe."""
    industry_rank: Optional[float] = None       # percentile in industry
    capability_rank: Optional[float] = None     # percentile in capability
    reputation_level: str = "N/A"               # A / B / C / D
    growth_stage: str = "position"              # position | selfknow | action | provision | accumulate | reputation
    business_rank: Optional[float] = None       # percentile in business value
    influence_score: float = 0.0                # 0-100


# ---- Trajectory: how the node arrived at this position ----

@dataclass
class NodeTrajectory:
    """The path a node took to reach its current position."""
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    stage_transitions: List[Dict[str, Any]] = field(default_factory=list)
    score_history: List[Dict[str, Any]] = field(default_factory=list)


# ---- UniverseNode: the base for all living nodes ----

class UniverseNode(ABC):
    """Base class for all nodes in the GEO Universe.

    Every node has a type registered in the UniverseRegistry,
    and carries Identity, Position, Trajectory, Memory, and Capabilities.

    Subclasses: Company, Provider, Industry, Capability, Person, Product, etc.
    """

    node_type: str = ""  # Must match a key in registry.yaml -> node_types

    def __init__(self, node_id: str = None, node_type: str = None):
        self.node_id = node_id or str(uuid.uuid4())
        self.node_type = node_type or self.__class__.node_type
        self.created_at = datetime.now(timezone.utc).isoformat()

        # Living properties
        self.identity: Dict[str, Any] = {}
        self.memory: List[Dict[str, Any]] = []
        self.observations: List[Dict[str, Any]] = []
        self.knowledge: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
        self.capabilities: List[str] = []

        self.position = NodePosition()
        self.trajectory = NodeTrajectory()

    # ---- Registry integration ----

    @property
    def meta(self):
        """Get this node type's metadata from the Registry."""
        return get_registry().get_node_type(self.node_type)

    @property
    def label(self) -> str:
        m = self.meta
        return m.label if m else self.node_type

    @property
    def color(self) -> str:
        m = self.meta
        return m.color if m else "#94a3b8"

    @property
    def size(self) -> int:
        m = self.meta
        return m.size if m else 14

    @property
    def layer(self) -> int:
        m = self.meta
        return m.layer if m else 99

    @property
    def allowed_capabilities(self) -> List[str]:
        m = self.meta
        return m.capabilities if m else []

    # ---- Identity ----

    def set_identity(self, profile: Dict[str, Any]):
        self.identity = profile

    def get_identity(self) -> Dict[str, Any]:
        return self.identity

    # ---- Memory ----

    def remember(self, event_type: str, payload: Dict[str, Any]):
        """Record a memory event in this node's timeline."""
        self.memory.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": payload,
        })

    def get_memory(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.memory[-limit:]

    # ---- Position ----

    def update_position(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.position, key):
                setattr(self.position, key, value)

    def get_position(self) -> NodePosition:
        return self.position

    # ---- Trajectory ----

    def record_milestone(self, description: str, data: Dict[str, Any] = None):
        self.trajectory.milestones.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "data": data or {},
        })

    def get_trajectory(self) -> NodeTrajectory:
        return self.trajectory

    # ---- Relationships ----

    def add_relationship(self, target_id: str, rel_type: str, data: Dict = None):
        self.relationships.append({
            "target_id": target_id,
            "type": rel_type,
            "data": data or {},
            "established": datetime.now(timezone.utc).isoformat(),
        })

    def get_relationships(self, rel_type: str = None) -> List[Dict]:
        if rel_type:
            return [r for r in self.relationships if r["type"] == rel_type]
        return self.relationships

    # ---- Capabilities ----

    def add_capability(self, cap_id: str):
        if cap_id not in self.capabilities:
            self.capabilities.append(cap_id)

    def has_capability(self, cap_id: str) -> bool:
        return cap_id in self.capabilities

    # ---- Summary (for frontend panel) ----

    def summary(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "color": self.color,
            "identity": self.identity,
            "position": {
                "industry_rank": self.position.industry_rank,
                "capability_rank": self.position.capability_rank,
                "reputation_level": self.position.reputation_level,
                "growth_stage": self.position.growth_stage,
                "influence_score": self.position.influence_score,
            },
            "capabilities": self.capabilities,
            "relationship_count": len(self.relationships),
            "memory_count": len(self.memory),
        }


# ---- Helper: determine if a type is valid ----

def is_valid_node_type(type_id: str) -> bool:
    """Check if a node type is registered in the UniverseRegistry."""
    return get_registry().get_node_type(type_id) is not None


def get_node_type_label(type_id: str, default: str = "") -> str:
    """Get the display label for a node type from the Registry."""
    return get_registry().get_node_type_label(type_id, default)


def get_node_type_color(type_id: str, default: str = "#94a3b8") -> str:
    return get_registry().get_node_type_color(type_id, default)
