# GEO Universe Decision Engine
# Phase C2: From "understanding the world" to "helping nodes change the world".
#
# The Decision Engine takes a NodeContext (from Context Engine) and generates
# multiple candidate decision paths. It does NOT make decisions for the user.
# It presents possibilities, each backed by: suitability score, basis, prerequisites,
# risks, and required capabilities.
#
# Principle: Universe shows possibilities. Users make decisions.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from functools import lru_cache
import uuid

from app.universe.registry import get_registry
from app.universe.context_engine import NodeContext, get_context_engine


@dataclass
class CandidatePath:
    """A single candidate decision path for a node.

    Not a command. Not a recommendation. A possibility map.
    """
    path_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""                      # e.g. "?? Data ??"
    category: str = ""                   # capability | certification | partnership | market | investment
    description: str = ""
    suitability_score: float = 0.0       # 0-1, how well this path fits the node
    basis: List[str] = field(default_factory=list)     # Why this path makes sense
    prerequisites: List[str] = field(default_factory=list)  # What's needed before starting
    required_capabilities: List[str] = field(default_factory=list)  # cap_ids needed
    expected_outcomes: List[str] = field(default_factory=list)  # What changes if followed
    risks: List[Dict[str, str]] = field(default_factory=list)    # [{severity, description}]
    timeframe_days: int = 90             # estimated completion time
    priority: int = 2                    # 1=urgent, 2=important, 3=optional
    next_action: str = ""                # concrete first step

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path_id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "suitability_score": round(self.suitability_score, 2),
            "basis": self.basis,
            "prerequisites": self.prerequisites,
            "required_capabilities": self.required_capabilities,
            "expected_outcomes": self.expected_outcomes,
            "risks": self.risks,
            "trust_feasibility": round(self.trust_feasibility, 2),
            "trust_risk_flags": self.trust_risk_flags,
            "timeframe_days": self.timeframe_days,
            "priority": self.priority,
            "next_action": self.next_action,
        }


@dataclass
class DecisionReport:
    """Complete decision analysis for a node.

    Contains multiple candidate paths ranked by suitability,
    plus a summary and clear rationale for each.
    """
    node_id: str
    node_type: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: str = ""
    current_situation: str = ""
    paths: List[CandidatePath] = field(default_factory=list)
    total_paths: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "generated_at": self.generated_at,
            "summary": self.summary,
            "current_situation": self.current_situation,
            "paths": [p.to_dict() for p in self.paths],
            "total_paths": self.total_paths,
            "ranked_by_suitability": [p.title for p in sorted(self.paths, key=lambda x: x.suitability_score, reverse=True)],
        }


class DecisionEngine:
    """Generates multi-path decision analysis from Context.

    Usage:
        engine = DecisionEngine.get_instance()
        ctx = context_engine.understand("comp-001", "company", ...)
        report = engine.decide(ctx)
        for path in report.paths:
            print(f"{path.title}: {path.suitability_score:.0%} suitable")
    """

    _instance: Optional["DecisionEngine"] = None

    # Decision templates by node_type ? each template evaluates multiple candidate paths
    DECISION_TEMPLATES: Dict[str, List[Dict]] = {
        "company": [
            {
                "category": "capability",
                "title_template": "?? {gap_capability} ??",
                "description_template": "?? {gap_capability} ????????????????",
                "score_weights": {"position_gap": 0.4, "future_signal": 0.3, "risk_urgency": 0.3},
            },
            {
                "category": "certification",
                "title_template": "?? {relevant_cert} ??",
                "description_template": "?????????? AI ??????",
                "score_weights": {"trust_gap": 0.5, "position_gap": 0.3, "timeframe": 0.2},
            },
            {
                "category": "partnership",
                "title_template": "????????",
                "description_template": "????????????????????????",
                "score_weights": {"network_gap": 0.5, "capability_synergy": 0.3, "future_signal": 0.2},
            },
            {
                "category": "market",
                "title_template": "?? {emerging_domain} ??",
                "description_template": "?????? {emerging_domain} ???????",
                "score_weights": {"future_signal": 0.5, "capability_readiness": 0.3, "risk_assessment": 0.2},
            },
            {
                "category": "capability",
                "title_template": "?? {weakest_capability} ?????",
                "description_template": "????????????????????",
                "score_weights": {"mastery_gap": 0.4, "market_value": 0.3, "competitor_benchmark": 0.3},
            },
        ],
        "provider": [
            {
                "category": "certification",
                "title_template": "????????",
                "description_template": "???????? AI ????????",
                "score_weights": {"trust_gap": 0.6, "market_demand": 0.4},
            },
            {
                "category": "capability",
                "title_template": "????????",
                "description_template": "????????????????",
                "score_weights": {"capability_diversity": 0.5, "market_signal": 0.5},
            },
            {
                "category": "partnership",
                "title_template": "???????????",
                "description_template": "?????????????????",
                "score_weights": {"network_gap": 0.4, "reputation_boost": 0.4, "risk_mitigation": 0.2},
            },
        ],
        "ai_agent": [
            {
                "category": "capability",
                "title_template": "?????????",
                "description_template": "??????? = ???????",
                "score_weights": {"core_capability_gap": 0.6, "future_signal": 0.4},
            },
            {
                "category": "capability",
                "title_template": "????????",
                "description_template": "????? AI ?????????",
                "score_weights": {"mastery_gap": 0.5, "trust_gap": 0.5},
            },
        ],
        "government": [
            {
                "category": "capability",
                "title_template": "????????",
                "description_template": "?????????????????",
                "score_weights": {"governance_gap": 0.6, "industry_need": 0.4},
            },
        ],
    }

    def __init__(self):
        self.registry = get_registry()
        self.context_engine = get_context_engine()

    @classmethod
    def get_instance(cls) -> "DecisionEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Public API ----

    def decide(self, ctx: NodeContext) -> DecisionReport:
        """Generate a multi-path decision analysis from a NodeContext.

        Returns a DecisionReport with ranked candidate paths.
        Each path includes: why it fits, what's needed, what risks exist.
        """
        report = DecisionReport(
            node_id=ctx.node_id,
            node_type=ctx.node_type,
            current_situation=ctx._generate_summary(),
        )

        templates = self.DECISION_TEMPLATES.get(ctx.node_type, self.DECISION_TEMPLATES.get("company", []))
        paths = []

        for template in templates:
            path = self._evaluate_template(template, ctx)
            if path.suitability_score > 0.1:  # Only include paths with some relevance
                paths.append(path)

        # Sort by suitability score descending
        paths.sort(key=lambda p: p.suitability_score, reverse=True)

        # Mark top 2 as priority 1 (urgent), next 2 as priority 2
        for i, p in enumerate(paths):
            if i < 2:
                p.priority = 1
            elif i < 4:
                p.priority = 2
            else:
                p.priority = 3

        report.paths = paths
        report.total_paths = len(paths)
        report.summary = self._generate_summary(ctx, paths)

        return report

    def decide_from_data(self, node_id: str, node_type: str,
                         extra_data: Dict[str, Any] = None) -> DecisionReport:
        """Convenience: generate context + decide in one call."""
        ctx = self.context_engine.understand(node_id, node_type, extra_data or {})
        return self.decide(ctx)

    # ---- Template Evaluation ----

    def _evaluate_template(self, template: Dict, ctx: NodeContext) -> CandidatePath:
        """Evaluate a decision template against a node's context and produce a scored path."""
        category = template["category"]
        weights = template.get("score_weights", {})

        # Build the path
        path = CandidatePath(
            category=category,
            title=template["title_template"],
            description=template["description_template"],
        )

        # Evaluate each score factor
        scores = {}

        # Position gap: how far from ideal position
        pos = ctx.current_position.get("position", {})
        if pos.get("industry_rank") is not None:
            scores["position_gap"] = min(pos["industry_rank"], 1.0)  # Higher rank = bigger gap

        # Trust gap: reputation level mapped to gap
        rep_levels = {"A": 0.1, "B": 0.3, "C": 0.5, "D": 0.7, "E": 0.9, "N/A": 0.5}
        scores["trust_gap"] = rep_levels.get(pos.get("reputation_level", "N/A"), 0.5)

        # Network gap: how isolated the node is
        rels = ctx.relationship_context.get("total", 0)
        scores["network_gap"] = max(0, 1.0 - rels / 20.0)

        # Future signal: are there emerging concepts relevant?
        signals = ctx.future_signals.get("emerging_concepts", [])
        scores["future_signal"] = min(len(signals) * 0.15, 1.0)

        # Capability readiness: how many available next-step capabilities
        caps_next = ctx.capability_state.get("total_available", 0)
        scores["capability_readiness"] = min(caps_next * 0.1, 1.0) if caps_next > 0 else 0.0
        scores["capability_diversity"] = min(ctx.capability_state.get("total_acquired", 0) * 0.08, 1.0)

        # Mastery gap: inverse of average mastery level
        scores["mastery_gap"] = 0.5  # Default mid-level gap

        # Risk urgency: are there high-severity risks?
        has_high_risk = any(r.get("severity") == "high" for r in ctx.risk_assessment.get("risks", []))
        scores["risk_urgency"] = 1.0 if has_high_risk else 0.3

        # Competitor benchmark / market value (proxied from position)
        scores["market_value"] = 1.0 - min(pos.get("influence_score", 0) / 100.0, 1.0)
        scores["competitor_benchmark"] = 0.5
        scores["risk_assessment"] = 0.5
        scores["market_demand"] = 0.5
        scores["risk_mitigation"] = 0.5
        scores["reputation_boost"] = scores["trust_gap"]
        scores["core_capability_gap"] = 0.6
        scores["governance_gap"] = 0.5
        scores["industry_need"] = 0.5
        scores["capability_synergy"] = min(ctx.capability_state.get("total_acquired", 0) * 0.08, 1.0)
        scores["timeframe"] = 0.5

        # Compute suitability score from weighted factors
        total_weight = 0
        weighted_sum = 0
        for factor, weight in weights.items():
            if factor in scores:
                weighted_sum += scores[factor] * weight
                total_weight += weight

        if total_weight > 0:
            path.suitability_score = round(weighted_sum / total_weight, 2)
        else:
            path.suitability_score = 0.3

        # Fill in context-specific details

        # Basis: why this path makes sense
        basis = []
        if scores.get("position_gap", 0) > 0.3:
            basis.append(f"??????????? (top {pos.get('industry_rank', 1.0)*100:.0f}%)")
        if scores.get("trust_gap", 0) > 0.4:
            basis.append(f"????? {pos.get('reputation_level', 'N/A')}?????? AI ????")
        if scores.get("network_gap", 0) > 0.5:
            basis.append(f"?????? (? {rels} ???)")
        if signals:
            basis.append(f"???? {len(signals)} ???????")
        if has_high_risk:
            basis.append("????????????")
        if not basis:
            basis.append("?????????????")
        path.basis = basis

        # Prerequisites
        prereqs = []
        if pos.get("growth_stage") in ("position", "selfknow"):
            prereqs.append("??????????????")
        if ctx.capability_state.get("total_acquired", 0) < 3:
            prereqs.append("??????????? (3+ ?)")
        if not prereqs:
            prereqs.append("???????")
        path.prerequisites = prereqs

        # Required capabilities
        available = ctx.capability_state.get("available", [])
        if available:
            path.required_capabilities = [c.get("cap_id", c.get("label", "")) for c in available[:3]]
        else:
            path.required_capabilities = ["observe"]

        # Expected outcomes
        outcomes = []
        if pos.get("industry_rank") is not None:
            improved_rank = max(0.01, pos["industry_rank"] - 0.1)
            outcomes.append(f"????????? top {improved_rank*100:.0f}%")
        if pos.get("reputation_level") in ("C", "D", "E"):
            next_level = {"E": "D", "D": "C", "C": "B", "B": "A"}.get(pos["reputation_level"], "B")
            outcomes.append(f"????????? {next_level}")
        if path.category == "certification":
            outcomes.append("????????? AI ?????")
        if path.category == "partnership":
            outcomes.append("????????????????")
        if path.category == "market":
            outcomes.append("?????????")
        if not outcomes:
            outcomes.append("??????????????????")
        path.expected_outcomes = outcomes

        # Risks
        risks = []
        risks.append({"severity": "low", "description": "????????????????"})
        if path.category == "capability":
            risks.append({"severity": "medium", "description": "??????????????????????"})
        if path.category == "partnership":
            risks.append({"severity": "medium", "description": "??????????????"})
        if path.category == "market":
            risks.append({"severity": "high", "description": "???????????????????"})
        path.risks = risks

        # Timeframe estimate
        timeframes = {"capability": 60, "certification": 45, "partnership": 90, "market": 180, "investment": 120}
        path.timeframe_days = timeframes.get(path.category, 90)

        # Next action
        next_actions = {
            "capability": f"????????????? {path.required_capabilities[0] if path.required_capabilities else 'observe'} ??",
            "certification": "????????????????????",
            "partnership": f"?? 3-5 ???????????????",
            "market": "???????????????",
            "investment": "??????????????????",
        }
        path.next_action = next_actions.get(path.category, "?????????????")

        # Replace template variables in title/description
        gap_cap = path.required_capabilities[0] if path.required_capabilities else "observe"
        path.title = path.title.replace("{gap_capability}", gap_cap)
        path.title = path.title.replace("{weakest_capability}", gap_cap)
        path.title = path.title.replace("{relevant_cert}", "GEO ????")
        path.title = path.title.replace("{emerging_domain}", "AI ???")
        path.description = path.description.replace("{gap_capability}", gap_cap)
        path.description = path.description.replace("{emerging_domain}", "AI ???")

        return path

    # ---- Summary ----

    def _generate_summary(self, ctx: NodeContext, paths: List[CandidatePath]) -> str:
        if not paths:
            return "??????????????????"

        top = paths[0]
        name = ctx.identity.get("name", ctx.node_id[:8])
        stage = ctx.current_position.get("position", {}).get("growth_stage", "")
        rep = ctx.current_position.get("position", {}).get("reputation_level", "")

        lines = [
            f"{name} ???? {stage} ????? {rep}?",
            f"??? {len(paths)} ??????????????{top.title}????? {top.suitability_score:.0%}??",
            f"?? {top.timeframe_days} ???????????",
        ]
        return " ".join(lines)


@lru_cache()
def get_decision_engine() -> DecisionEngine:
    return DecisionEngine.get_instance()
