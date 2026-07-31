"""Universe Registry — Single source of truth for all node types, relationships,
views, capabilities, lifecycle stages, and their metadata.

Every module (UI, API, Agent, Renderer) queries this registry instead of
hardcoding colors, sizes, labels, icons, or type-specific behavior.
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from functools import lru_cache
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_REGISTRY_PATH = os.path.join(_PROJECT_ROOT, "config", "universe", "registry.yaml")


@dataclass
class NodeTypeMeta:
    """Metadata for a single node type."""
    type_id: str
    label: str
    label_en: str
    icon: str
    color: str
    glow: str
    size: int
    size_3d: float
    layer: int
    description: str
    capabilities: List[str] = field(default_factory=list)
    lifecycle_stages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_id": self.type_id,
            "label": self.label,
            "label_en": self.label_en,
            "icon": self.icon,
            "color": self.color,
            "glow": self.glow,
            "size": self.size,
            "size_3d": self.size_3d,
            "layer": self.layer,
            "description": self.description,
            "capabilities": self.capabilities,
            "lifecycle_stages": self.lifecycle_stages,
        }


@dataclass
class RelationshipTypeMeta:
    type_id: str
    label: str
    label_en: str
    color: str
    bidirectional: bool
    allowed_pairs: List[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_id": self.type_id,
            "label": self.label,
            "label_en": self.label_en,
            "color": self.color,
            "bidirectional": self.bidirectional,
            "allowed_pairs": self.allowed_pairs,
        }


@dataclass
class ViewMeta:
    view_id: str
    label: str
    label_en: str
    question: str
    question_en: str
    icon: str
    description: str
    layout_2d: str
    layout_3d: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "view_id": self.view_id,
            "label": self.label,
            "label_en": self.label_en,
            "question": self.question,
            "question_en": self.question_en,
            "icon": self.icon,
            "description": self.description,
            "layout_2d": self.layout_2d,
            "layout_3d": self.layout_3d,
        }


@dataclass
class LifecycleStageMeta:
    key: str
    label: str
    label_en: str
    icon: str
    order: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "label_en": self.label_en,
            "icon": self.icon,
            "order": self.order,
            "description": self.description,
        }


class UniverseRegistry:
    """Central registry — single source of truth for all type metadata.

    Usage:
        reg = UniverseRegistry.get_instance()
        company_meta = reg.get_node_type("company")
        views = reg.list_views()
    """

    _instance: Optional["UniverseRegistry"] = None

    def __init__(self, config_path: str = _REGISTRY_PATH):
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        self.version = raw.get("version", "unknown")
        self.description = raw.get("description", "")

        # Parse node types
        self._node_types: Dict[str, NodeTypeMeta] = {}
        for type_id, meta in raw.get("node_types", {}).items():
            self._node_types[type_id] = NodeTypeMeta(
                type_id=type_id,
                label=meta.get("label", type_id),
                label_en=meta.get("label_en", type_id),
                icon=meta.get("icon", ""),
                color=meta.get("color", "#94a3b8"),
                glow=meta.get("glow", "#94a3b8"),
                size=meta.get("size", 14),
                size_3d=meta.get("size_3d", 0.4),
                layer=meta.get("layer", 99),
                description=meta.get("description", ""),
                capabilities=meta.get("capabilities", []),
                lifecycle_stages=meta.get("lifecycle_stages", []),
            )

        # Parse relationship types
        self._rel_types: Dict[str, RelationshipTypeMeta] = {}
        for type_id, meta in raw.get("relationship_types", {}).items():
            self._rel_types[type_id] = RelationshipTypeMeta(
                type_id=type_id,
                label=meta.get("label", type_id),
                label_en=meta.get("label_en", type_id),
                color=meta.get("color", "#94a3b8"),
                bidirectional=meta.get("bidirectional", False),
                allowed_pairs=meta.get("allowed_pairs", []),
            )

        # Parse views
        self._views: Dict[str, ViewMeta] = {}
        for view_id, meta in raw.get("views", {}).items():
            self._views[view_id] = ViewMeta(
                view_id=view_id,
                label=meta.get("label", view_id),
                label_en=meta.get("label_en", view_id),
                question=meta.get("question", ""),
                question_en=meta.get("question_en", ""),
                icon=meta.get("icon", ""),
                description=meta.get("description", ""),
                layout_2d=meta.get("layout_2d", "cose"),
                layout_3d=meta.get("layout_3d", "spherical"),
            )

        # Parse lifecycle stages
        self._lifecycle: List[LifecycleStageMeta] = []
        for stage in raw.get("lifecycle", {}).get("stages", []):
            self._lifecycle.append(LifecycleStageMeta(
                key=stage.get("key", ""),
                label=stage.get("label", ""),
                label_en=stage.get("label_en", ""),
                icon=stage.get("icon", ""),
                order=stage.get("order", 0),
                description=stage.get("description", ""),
            ))
        self._lifecycle.sort(key=lambda s: s.order)

        # Raw capability catalog
        self._capability_catalog: List[Dict[str, Any]] = raw.get("capability_catalog", [])

    @classmethod
    def get_instance(cls) -> "UniverseRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Node Types ----

    def get_node_type(self, type_id: str) -> Optional[NodeTypeMeta]:
        return self._node_types.get(type_id)

    def list_node_types(self) -> List[NodeTypeMeta]:
        return sorted(self._node_types.values(), key=lambda t: t.layer)

    def get_node_type_color(self, type_id: str, default: str = "#94a3b8") -> str:
        meta = self._node_types.get(type_id)
        return meta.color if meta else default

    def get_node_type_glow(self, type_id: str, default: str = "#94a3b8") -> str:
        meta = self._node_types.get(type_id)
        return meta.glow if meta else default

    def get_node_type_size(self, type_id: str, default: int = 14) -> int:
        meta = self._node_types.get(type_id)
        return meta.size if meta else default

    def get_node_type_size_3d(self, type_id: str, default: float = 0.4) -> float:
        meta = self._node_types.get(type_id)
        return meta.size_3d if meta else default

    def get_node_type_label(self, type_id: str, default: str = "") -> str:
        meta = self._node_types.get(type_id)
        return meta.label if meta else default

    def get_node_type_icon(self, type_id: str, default: str = "") -> str:
        meta = self._node_types.get(type_id)
        return meta.icon if meta else default

    # ---- Relationship Types ----

    def get_relationship_type(self, type_id: str) -> Optional[RelationshipTypeMeta]:
        return self._rel_types.get(type_id)

    def list_relationship_types(self) -> List[RelationshipTypeMeta]:
        return sorted(self._rel_types.values(), key=lambda r: r.type_id)

    def get_allowed_relationships_for(self, node_type: str) -> List[RelationshipTypeMeta]:
        return [
            rel for rel in self._rel_types.values()
            if any(node_type in pair for pair in rel.allowed_pairs)
        ]

    # ---- Views ----

    def get_view(self, view_id: str) -> Optional[ViewMeta]:
        return self._views.get(view_id)

    def list_views(self) -> List[ViewMeta]:
        return list(self._views.values())

    # ---- Lifecycle ----

    def list_lifecycle_stages(self) -> List[LifecycleStageMeta]:
        return self._lifecycle

    def get_lifecycle_stage(self, key: str) -> Optional[LifecycleStageMeta]:
        for s in self._lifecycle:
            if s.key == key:
                return s
        return None

    # ---- Capability Catalog ----

    def list_capabilities(self) -> List[Dict[str, Any]]:
        return self._capability_catalog

    def get_capability(self, cap_id: str) -> Optional[Dict[str, Any]]:
        for cap in self._capability_catalog:
            if cap.get("id") == cap_id:
                return cap
        return None

    # ---- Full Export ----

    def export_full(self) -> Dict[str, Any]:
        """Export the complete registry as a JSON-serializable dict.
        This is what the frontend API endpoint returns."""
        return {
            "version": self.version,
            "description": self.description,
            "node_types": {tid: t.to_dict() for tid, t in self._node_types.items()},
            "relationship_types": {tid: r.to_dict() for tid, r in self._rel_types.items()},
            "views": {vid: v.to_dict() for vid, v in self._views.items()},
            "lifecycle": [s.to_dict() for s in self._lifecycle],
            "capabilities": self._capability_catalog,
        }


@lru_cache()
def get_registry() -> UniverseRegistry:
    return UniverseRegistry.get_instance()
