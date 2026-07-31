# GEO Universe Capability Engine
# Capability Registry ? decouples node types from capabilities.
#
# Any node can possess any set of capabilities regardless of its type.
# Capabilities are the "verbs" of the Universe: observe, learn, certify, trade, etc.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from functools import lru_cache
from datetime import datetime, timezone
import uuid

from app.universe.registry import get_registry


@dataclass
class Capability:
    """A single capability that any node type can possess."""
    cap_id: str
    label: str
    label_en: str
    category: str                    # core | operation | trust | growth | connection
    description: str
    requires: List[str] = field(default_factory=list)     # prerequisite cap_ids
    enables: List[str] = field(default_factory=list)      # cap_ids this unlocks
    level: int = 1                   # 1=basic, 2=advanced, 3=expert
    auto_grant: bool = False         # True if automatically granted based on node_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cap_id": self.cap_id,
            "label": self.label,
            "label_en": self.label_en,
            "category": self.category,
            "description": self.description,
            "requires": self.requires,
            "enables": self.enables,
            "level": self.level,
        }


# The universal capability catalog ? NOT tied to any node type
UNIVERSAL_CAPABILITIES = [
    Capability("observe", "Observe", "??", "core",
               "???????????", enables=["learn", "report"], level=1, auto_grant=True),
    Capability("learn", "Learn", "??", "core",
               "???????????", requires=["observe"], enables=["adapt", "teach"], level=1),
    Capability("adapt", "Adapt", "??", "core",
               "?????????????", requires=["learn"], enables=["evolve"], level=2),
    Capability("evolve", "Evolve", "??", "core",
               "?????????????", requires=["adapt"], level=3),
    Capability("certify", "Certify", "??", "trust",
               "?????????", enables=["verify"], level=1),
    Capability("verify", "Verify", "??", "trust",
               "??????????????", requires=["certify"], level=2),
    Capability("trade", "Trade", "??", "operation",
               "??????", enables=["finance"], level=1),
    Capability("finance", "Finance", "??", "operation",
               "????????????", requires=["trade"], level=2),
    Capability("connect", "Connect", "??", "connection",
               "?????????", enables=["collaborate", "match"], level=1),
    Capability("collaborate", "Collaborate", "??", "connection",
               "??????", requires=["connect"], level=2),
    Capability("match", "Match", "??", "connection",
               "?????????????", requires=["connect"], enables=["recommend"], level=2),
    Capability("recommend", "Recommend", "??", "connection",
               "????????????", requires=["match"], level=3),
    Capability("teach", "Teach", "??", "growth",
               "????????????", requires=["learn"], level=2),
    Capability("build", "Build", "??", "operation",
               "?????????????", enables=["serve"], level=1),
    Capability("serve", "Serve", "??", "operation",
               "????????????", requires=["build"], level=2),
    Capability("govern", "Govern", "??", "trust",
               "??????????", enables=["regulate"], level=1),
    Capability("regulate", "Regulate", "??", "trust",
               "??????????", requires=["govern"], level=2),
    Capability("research", "Research", "??", "growth",
               "?????????", enables=["report"], level=1),
    Capability("report", "Report", "??", "growth",
               "?????????", requires=["observe", "research"], level=2),
    Capability("invest", "Invest", "??", "operation",
               "???????????", requires=["trade"], level=3),
]


class CapabilityRegistry:
    """Central registry for capabilities ? decoupled from node types.

    Any node can acquire any capability. The registry tracks:
      - What capabilities exist in the Universe
      - Which nodes have which capabilities
      - Capability prerequisites and unlocks
      - Capability levels and categories

    Usage:
        cr = CapabilityRegistry.get_instance()
        cr.grant(node_id="comp-001", cap_id="certify")
        available = cr.get_available_for("comp-001")
    """

    _instance: Optional["CapabilityRegistry"] = None

    def __init__(self):
        # Universal catalog (all possible capabilities)
        self._catalog: Dict[str, Capability] = {
            c.cap_id: c for c in UNIVERSAL_CAPABILITIES
        }

        # Node-to-capability assignments
        self._node_caps: Dict[str, Set[str]] = {}
        self._mastery: Dict[str, Dict[str, Dict]] = {}  # node_id -> {cap_id: {level, evidence, outcome}}

        # Capability-auto-grant based on node_type
        self._type_defaults: Dict[str, List[str]] = {
            "company": ["observe", "trade", "build", "connect"],
            "provider": ["observe", "serve", "connect", "certify"],
            "government": ["observe", "govern", "regulate", "certify"],
            "person": ["observe", "learn", "connect"],
            "ai_agent": ["observe", "learn", "adapt", "serve", "recommend"],
            "knowledge": ["observe", "research", "report"],
            "policy": ["observe", "govern", "regulate"],
            "industry": ["observe"],
        }

    @classmethod
    def get_instance(cls) -> "CapabilityRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Catalog ----

    def get_capability(self, cap_id: str) -> Optional[Capability]:
        return self._catalog.get(cap_id)

    def list_all_capabilities(self) -> List[Capability]:
        return sorted(self._catalog.values(), key=lambda c: (c.category, c.level))

    def list_by_category(self, category: str) -> List[Capability]:
        return [c for c in self._catalog.values() if c.category == category]

    def list_by_level(self, level: int) -> List[Capability]:
        return [c for c in self._catalog.values() if c.level == level]

    # ---- Grant / Revoke ----

    def grant(self, node_id: str, cap_id: str) -> bool:
        """Grant a capability to a node."""
        if cap_id not in self._catalog:
            return False
        if node_id not in self._node_caps:
            self._node_caps[node_id] = set()
        self._node_caps[node_id].add(cap_id)
        return True

    def grant_defaults(self, node_id: str, node_type: str):
        """Grant the default capabilities for a node type."""
        defaults = self._type_defaults.get(node_type, [])
        for cap_id in defaults:
            self.grant(node_id, cap_id)

    def revoke(self, node_id: str, cap_id: str) -> bool:
        if node_id in self._node_caps:
            self._node_caps[node_id].discard(cap_id)
            return True
        return False

    # ---- Query ----

    def get_node_capabilities(self, node_id: str) -> List[str]:
        return sorted(list(self._node_caps.get(node_id, set())))

    def has_capability(self, node_id: str, cap_id: str) -> bool:
        return cap_id in self._node_caps.get(node_id, set())

    def get_nodes_with_capability(self, cap_id: str) -> List[str]:
        return [nid for nid, caps in self._node_caps.items() if cap_id in caps]

    # ---- Progression ----

    def get_available_for(self, node_id: str) -> List[Capability]:
        """Get capabilities a node can acquire next (prerequisites met)."""
        current = self._node_caps.get(node_id, set())
        available = []
        for cap in self._catalog.values():
            if cap.cap_id in current:
                continue
            if all(req in current for req in cap.requires):
                available.append(cap)
        return sorted(available, key=lambda c: (c.category, c.level))

    def get_skill_tree(self, node_id: str) -> Dict[str, Any]:
        """Get a complete skill tree: acquired, available, locked."""
        current = self._node_caps.get(node_id, set())
        available = self.get_available_for(node_id)
        locked = [c for c in self._catalog.values()
                  if c.cap_id not in current and c not in available]

        return {
            "node_id": node_id,
            "acquired": [{"cap_id": c.cap_id, "label": c.label, "level": c.level}
                         for cid in current if cid in self._catalog
                         for c in [self._catalog[cid]]],
            "available": [{"cap_id": c.cap_id, "label": c.label, "level": c.level,
                           "requires": c.requires}
                          for c in available],
            "locked": [{"cap_id": c.cap_id, "label": c.label, "level": c.level}
                       for c in locked[:10]],
            "total_acquired": len(current),
            "total_available": len(available),
        }


    # ---- Mastery (Capability depth, not just labels) ----

    def set_mastery(self, node_id: str, cap_id: str, level: int = 1,
                    evidence_count: int = 0, outcome: str = "",
                    trust_level: str = "C") -> bool:
        """Set the mastery level for a node's capability with evidence backing."""
        if cap_id not in self._catalog or node_id not in self._node_caps:
            return False
        if cap_id not in self._node_caps[node_id]:
            self.grant(node_id, cap_id)
        if node_id not in self._mastery:
            self._mastery[node_id] = {}
        self._mastery[node_id][cap_id] = {
            "level": level,
            "evidence_count": evidence_count,
            "outcome": outcome,
            "trust_level": trust_level,
            "assessed_at": datetime.now(timezone.utc).isoformat(),
        }
        return True

    def get_mastery(self, node_id: str, cap_id: str) -> Optional[Dict]:
        """Get the mastery details for a node's capability."""
        return self._mastery.get(node_id, {}).get(cap_id)

    def get_node_mastery_profile(self, node_id: str) -> Dict[str, Any]:
        """Get the complete mastery profile for a node."""
        caps = self.get_node_capabilities(node_id)
        mastery = {}
        for cid in caps:
            cap = self._catalog.get(cid)
            m = self._mastery.get(node_id, {}).get(cid, {})
            mastery[cid] = {
                "capability": cap.label if cap else cid,
                "category": cap.category if cap else "",
                "level": m.get("level", 1),
                "evidence_count": m.get("evidence_count", 0),
                "outcome": m.get("outcome", ""),
                "trust_level": m.get("trust_level", "C"),
            }
        return {
            "node_id": node_id,
            "total_capabilities": len(caps),
            "mastery_levels": {
                "expert": sum(1 for m in mastery.values() if m["level"] >= 3),
                "advanced": sum(1 for m in mastery.values() if m["level"] == 2),
                "basic": sum(1 for m in mastery.values() if m["level"] == 1),
            },
            "average_trust": self._avg_trust(mastery),
            "capabilities": mastery,
        }

    def _avg_trust(self, mastery: Dict) -> str:
        if not mastery:
            return "N/A"
        scores = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
        total = sum(scores.get(m["trust_level"], 3) for m in mastery.values())
        avg = total / len(mastery)
        for letter, score in scores.items():
            if avg >= score:
                return letter
        return "C"

    # ---- Stats ----


    def stats(self) -> Dict[str, Any]:
        return {
            "total_capabilities": len(self._catalog),
            "categories": list(set(c.category for c in self._catalog.values())),
            "nodes_with_capabilities": len(self._node_caps),
            "most_common": sorted(
                [(cid, len(self.get_nodes_with_capability(cid)))
                 for cid in self._catalog],
                key=lambda x: x[1], reverse=True
            )[:5],
        }

    def export_full(self) -> Dict[str, Any]:
        return {
            "catalog": [c.to_dict() for c in self._catalog.values()],
            "categories": list(set(c.category for c in self._catalog.values())),
            "stats": self.stats(),
        }


@lru_cache()
def get_capability_registry() -> CapabilityRegistry:
    return CapabilityRegistry.get_instance()
