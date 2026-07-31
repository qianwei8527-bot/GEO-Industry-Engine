# GEO Universe Position Engine
# Capability 1: Position ? know yourself.
#
# The Position Engine computes real-time coordinates for any node type.
# It is NOT a scoring tool. It answers "Where am I?" across 6 dimensions:
#   industry_rank, capability_rank, reputation_level, growth_stage,
#   business_rank, influence_score

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from functools import lru_cache

from app.universe.registry import get_registry
from app.core.config_loader import ConfigLoader, config_loader


@dataclass
class PositionReport:
    """A complete position assessment for one node."""
    node_id: str
    node_type: str
    computed_at: str = ""

    # Six dimensions
    industry_rank: Optional[float] = None      # percentile in industry (0.01 = top 1%)
    capability_rank: Optional[float] = None    # percentile in capability
    reputation_level: str = "N/A"              # A / B / C / D / E
    growth_stage: str = "position"             # position|selfknow|action|provision|accumulate|reputation
    business_rank: Optional[float] = None      # percentile in business value
    influence_score: float = 0.0               # 0-100

    # Raw inputs used for computation
    evidence_count: int = 0
    relationship_count: int = 0
    capability_count: int = 0
    certification_count: int = 0
    trust_score: float = 0.0

    # Interpretation
    narrative: str = ""
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    suggested_stage: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "computed_at": self.computed_at,
            "position": {
                "industry_rank": self.industry_rank,
                "capability_rank": self.capability_rank,
                "reputation_level": self.reputation_level,
                "growth_stage": self.growth_stage,
                "business_rank": self.business_rank,
                "influence_score": self.influence_score,
            },
            "inputs": {
                "evidence_count": self.evidence_count,
                "relationship_count": self.relationship_count,
                "capability_count": self.capability_count,
                "certification_count": self.certification_count,
                "trust_score": self.trust_score,
            },
            "interpretation": {
                "narrative": self.narrative,
                "strengths": self.strengths,
                "gaps": self.gaps,
                "suggested_stage": self.suggested_stage,
            },
        }


class PositionEngine:
    """Computes multi-dimensional position for any Universe node.

    Usage:
        engine = PositionEngine.get_instance()
        report = engine.compute(node_id="...", node_type="company", data={...})
        print(report.narrative)
    """

    _instance: Optional["PositionEngine"] = None

    # Thresholds for reputation levels
    REPUTATION_THRESHOLDS = {
        "A": (80, 100),
        "B": (60, 79),
        "C": (40, 59),
        "D": (20, 39),
        "E": (0, 19),
    }

    # Growth stage thresholds based on capability + relationship maturity
    STAGE_THRESHOLDS = {
        "reputation": 85,
        "accumulate": 65,
        "provision": 45,
        "action": 25,
        "selfknow": 10,
        "position": 0,
    }

    def __init__(self):
        self.registry = get_registry()
        self.config = config_loader

    @classmethod
    def get_instance(cls) -> "PositionEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Public API ----

    def compute(self, node_id: str, node_type: str, data: Dict[str, Any]) -> PositionReport:
        """Compute position for a node given its type and raw data.

        data should contain:
          - evidence_count, relationship_count, capability_count
          - certification_count, trust_score
          - geo_score (optional, from detection)
          - any type-specific metrics
        """
        from datetime import datetime, timezone

        node_meta = self.registry.get_node_type(node_type)
        if not node_meta:
            raise ValueError(f"Unknown node type: {node_type}")

        report = PositionReport(
            node_id=node_id,
            node_type=node_type,
            computed_at=datetime.now(timezone.utc).isoformat(),
            evidence_count=data.get("evidence_count", 0),
            relationship_count=data.get("relationship_count", 0),
            capability_count=data.get("capability_count", 0),
            certification_count=data.get("certification_count", 0),
            trust_score=data.get("trust_score", 0),
        )

        # Compute each dimension based on node type
        self._compute_industry_rank(report, data, node_meta)
        self._compute_capability_rank(report, data, node_meta)
        self._compute_reputation(report, data, node_meta)
        self._compute_growth_stage(report, data, node_meta)
        self._compute_business_rank(report, data, node_meta)
        self._compute_influence(report, data, node_meta)

        # Generate narrative interpretation
        self._generate_narrative(report, node_meta)

        return report

    def compute_from_node(self, node: Any) -> PositionReport:
        """Convenience: compute position from a UniverseNode or SQLAlchemy model."""
        data = {}

        # Extract from UniverseNode
        if hasattr(node, "summary"):
            s = node.summary()
            data["capability_count"] = len(s.get("capabilities", []))
            data["relationship_count"] = s.get("relationship_count", 0)
            data["evidence_count"] = s.get("memory_count", 0)
            if s.get("position"):
                data["trust_score"] = s["position"].get("influence_score", 0)

        # Extract from SQLAlchemy model
        for attr in ["evidence_count", "relationship_count", "capability_count",
                      "certification_count", "trust_score", "geo_score",
                      "reputation_score", "industry_rank"]:
            if hasattr(node, attr):
                val = getattr(node, attr)
                if val is not None:
                    data[attr] = val

        node_type = ""
        node_id = ""
        if hasattr(node, "node_type"):
            node_type = node.node_type
        elif hasattr(node, "entity_type"):
            node_type = node.entity_type
        if hasattr(node, "node_id"):
            node_id = node.node_id
        elif hasattr(node, "id"):
            node_id = str(node.id)

        return self.compute(node_id, node_type, data)

    # ---- Dimension Computers ----

    def _compute_industry_rank(self, report: PositionReport, data: Dict, meta):
        """Industry rank is a percentile based on combined capability + evidence + trust."""
        if "can_own_capabilities" not in meta.capabilities and "can_form_relationships" not in meta.capabilities:
            report.industry_rank = None
            return

        # Weighted composite
        evidence_w = self._get_weight("industry_rank", "evidence", 0.3)
        capability_w = self._get_weight("industry_rank", "capability", 0.3)
        trust_w = self._get_weight("industry_rank", "trust", 0.4)

        evidence_score = min(data.get("evidence_count", 0) / 50.0, 1.0)
        capability_score = min(data.get("capability_count", 0) / 10.0, 1.0)
        trust_score = data.get("trust_score", 0) / 100.0

        composite = evidence_score * evidence_w + capability_score * capability_w + trust_score * trust_w
        # Convert to percentile (higher composite = lower percentile)
        report.industry_rank = round(max(0.01, 1.0 - composite), 2)

    def _compute_capability_rank(self, report: PositionReport, data: Dict, meta):
        """Capability rank is based on certification + capability diversity."""
        if "can_be_certified" not in meta.capabilities and "can_own_capabilities" not in meta.capabilities:
            report.capability_rank = None
            return

        cert_score = min(data.get("certification_count", 0) / 5.0, 1.0)
        cap_score = min(data.get("capability_count", 0) / 10.0, 1.0)
        composite = cert_score * 0.5 + cap_score * 0.5
        report.capability_rank = round(max(0.01, 1.0 - composite), 2)

    def _compute_reputation(self, report: PositionReport, data: Dict, meta):
        """Reputation is letter grade based on trust + evidence + relationship quality."""
        if "can_earn_reputation" not in meta.capabilities:
            report.reputation_level = "N/A"
            return

        trust = data.get("trust_score", 0)
        evidence_bonus = min(data.get("evidence_count", 0), 20)
        relationship_bonus = min(data.get("relationship_count", 0), 10)

        score = trust + evidence_bonus * 0.5 + relationship_bonus * 1.0
        for level, (low, high) in self.REPUTATION_THRESHOLDS.items():
            if low <= score <= high:
                report.reputation_level = level
                break
        else:
            report.reputation_level = "E"

    def _compute_growth_stage(self, report: PositionReport, data: Dict, meta):
        """Growth stage based on capability + relationship + evidence maturity."""
        if "can_evolve" not in meta.capabilities and "can_own_capabilities" not in meta.capabilities:
            report.growth_stage = "position"
            return

        cap_score = min(data.get("capability_count", 0) * 10, 50)
        rel_score = min(data.get("relationship_count", 0) * 5, 30)
        ev_score = min(data.get("evidence_count", 0) * 2, 20)
        total = cap_score + rel_score + ev_score

        for stage, threshold in sorted(self.STAGE_THRESHOLDS.items(),
                                       key=lambda x: x[1], reverse=True):
            if total >= threshold:
                report.growth_stage = stage
                break

    def _compute_business_rank(self, report: PositionReport, data: Dict, meta):
        """Business rank is the node's commercial position (for tradable types)."""
        if "can_trade" not in meta.capabilities:
            report.business_rank = None
            return

        geo_score = data.get("geo_score", 0)
        trust = data.get("trust_score", 0)
        composite = geo_score * 0.6 + trust * 0.4
        report.business_rank = round(max(0.01, 1.0 - composite / 100.0), 2)

    def _compute_influence(self, report: PositionReport, data: Dict, meta):
        """Influence is a 0-100 score based on reach: relationships + evidence + certification."""
        rel_score = min(data.get("relationship_count", 0) * 3, 30)
        ev_score = min(data.get("evidence_count", 0) * 2, 30)
        cert_score = min(data.get("certification_count", 0) * 10, 20)
        trust_score = min(data.get("trust_score", 0) * 0.2, 20)
        report.influence_score = round(min(rel_score + ev_score + cert_score + trust_score, 100), 1)

    # ---- Narrative ----

    def _generate_narrative(self, report: PositionReport, meta):
        """Generate human-readable interpretation of the position report."""
        node_label = meta.label

        # Strengths
        strengths = []
        if report.reputation_level in ("A", "B"):
            strengths.append(f"High reputation ({report.reputation_level} level)")
        if report.capability_count >= 5:
            strengths.append(f"Broad capability set ({report.capability_count} capabilities)")
        if report.relationship_count >= 10:
            strengths.append(f"Strong connection network ({report.relationship_count} relationships)")
        if report.certification_count >= 2:
            strengths.append(f"Verified credentials ({report.certification_count} certifications)")
        if report.influence_score >= 60:
            strengths.append(f"Strong ecosystem influence (score: {report.influence_score})")

        # Gaps
        gaps = []
        if report.reputation_level in ("D", "E"):
            gaps.append("Need to build reputation through evidence and certifications")
        if report.capability_count < 3:
            gaps.append("Limited capability coverage ? consider adding key capabilities")
        if report.relationship_count < 3:
            gaps.append("Sparse connections ? expand partnership network")
        if report.evidence_count < 5:
            gaps.append("Low evidence count ? increase verifiable outputs")
        if report.growth_stage in ("position", "selfknow"):
            gaps.append("Early growth stage ? focus on capability building")

        # Narrative
        if report.industry_rank is not None and report.industry_rank <= 0.05:
            narrative = f"This {node_label} is in the top 5% of its industry ? a recognized leader."
        elif report.industry_rank is not None and report.industry_rank <= 0.20:
            narrative = f"This {node_label} is in the top 20% ? a strong, growing player."
        elif report.industry_rank is not None and report.industry_rank <= 0.50:
            narrative = f"This {node_label} is mid-tier, with room to grow through capability and reputation."
        else:
            narrative = f"This {node_label} is early-stage. Focus on building capabilities, evidence, and connections."

        # Suggested next stage
        stage_order = ["position", "selfknow", "action", "provision", "accumulate", "reputation"]
        current_idx = stage_order.index(report.growth_stage) if report.growth_stage in stage_order else 0
        suggested = stage_order[min(current_idx + 1, len(stage_order) - 1)] if current_idx < len(stage_order) - 1 else report.growth_stage

        report.narrative = narrative
        report.strengths = strengths if strengths else ["Building foundation"]
        report.gaps = gaps if gaps else ["Continue current trajectory"]
        report.suggested_stage = suggested

    # ---- Helpers ----

    def _get_weight(self, dimension: str, factor: str, default: float) -> float:
        """Get weight from scoring config or fall back to default."""
        try:
            weights = self.config.get_all_weights("assessment")
            return weights.get(f"{dimension}_{factor}", default)
        except Exception:
            return default


@lru_cache()
def get_position_engine() -> PositionEngine:
    return PositionEngine.get_instance()
