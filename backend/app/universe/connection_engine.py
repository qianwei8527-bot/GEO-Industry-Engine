# GEO Universe Future Connection Engine
# Phase C4: Connection based on shared future paths, not tag matching.
#
# Traditional B2B: "A needs B -> match B"
# GEO Universe:    "A has future goal state -> find nodes that fill path gaps"
#
# Completes the four core values: Position + Trajectory + Possibility + Connection

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from functools import lru_cache
import uuid

from app.universe.registry import get_registry
from app.universe.context_engine import get_context_engine
from app.universe.possibility_engine import (
    PossibilityEngine, PossibilityGraph, get_possibility_engine,
    DecisionMemory,
)
from app.universe.future_registry import get_future_registry


# ---- Data Classes ----

@dataclass
class ConnectionNeed:
    """A gap in a node's future path that requires external connection."""
    need_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_node_id: str = ""
    future_state_label: str = ""
    needed_capability: str = ""
    needed_node_type: str = ""
    urgency: str = "medium"             # critical | high | medium | low
    reason: str = ""
    current_gap_score: float = 0.0

    def to_dict(self):
        return {
            "need_id": self.need_id,
            "source_node_id": self.source_node_id,
            "future_state": self.future_state_label,
            "needed_capability": self.needed_capability,
            "needed_node_type": self.needed_node_type,
            "urgency": self.urgency,
            "reason": self.reason,
            "current_gap_score": round(self.current_gap_score, 2),
        }


@dataclass
class ConnectionCandidate:
    """A potential partner node that can help reach a future state.

    Scored using Future Alignment Score (5 factors), not generic match score.
    """
    candidate_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    candidate_node_id: str = ""
    candidate_node_type: str = ""
    candidate_name: str = ""
    candidate_label: str = ""
    future_alignment_score: float = 0.0
    capability_complementarity: float = 0.0
    trust_compatibility: float = 0.0
    historical_outcome_factor: float = 0.5
    network_position_bonus: float = 0.0
    connected_future_state: str = ""
    edge_strength: str = ""             # strong | moderate | weak
    recommendation: str = ""

    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "node_id": self.candidate_node_id,
            "node_type": self.candidate_node_type,
            "name": self.candidate_name,
            "label": self.candidate_label,
            "future_alignment_score": round(self.future_alignment_score, 2),
            "factors": {
                "capability_complementarity": round(self.capability_complementarity, 2),
                "trust_compatibility": round(self.trust_compatibility, 2),
                "historical_outcome": round(self.historical_outcome_factor, 2),
                "network_position": round(self.network_position_bonus, 2),
            },
            "connects_to_future": self.connected_future_state,
            "edge_strength": self.edge_strength,
            "recommendation": self.recommendation,
        }


@dataclass
class ConnectionReport:
    """Complete connection analysis for a node's future paths."""
    node_id: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    current_state: str = ""
    target_future_states: List[str] = field(default_factory=list)
    needs: List[ConnectionNeed] = field(default_factory=list)
    candidates: List[ConnectionCandidate] = field(default_factory=list)
    summary: str = ""

    def to_dict(self):
        sorted_candidates = sorted(
            self.candidates, key=lambda x: x.future_alignment_score, reverse=True
        )
        return {
            "node_id": self.node_id,
            "generated_at": self.generated_at,
            "current_state": self.current_state,
            "target_futures": self.target_future_states,
            "needs": [n.to_dict() for n in self.needs],
            "candidates": [c.to_dict() for c in sorted_candidates],
            "candidate_count": len(sorted_candidates),
            "summary": self.summary,
            "by_future_state": self._group_by_future(),
        }

    def _group_by_future(self):
        groups = {}
        for c in self.candidates:
            key = c.connected_future_state or "general"
            if key not in groups:
                groups[key] = {"candidates": [], "avg_score": 0}
            groups[key]["candidates"].append(c.to_dict())
        for key, g in groups.items():
            scores = [x.get("future_alignment_score", 0) for x in g["candidates"]]
            g["avg_score"] = round(sum(scores) / max(len(scores), 1), 2)
            g["count"] = len(scores)
        return groups


# ---- Connection Engine ----

class FutureConnectionEngine:
    """Discovers nodes that can help a target node reach its future states.

    Principle: Connection exists to enter shared future paths together.

    Usage:
        engine = FutureConnectionEngine.get_instance()
        report = engine.discover_connections("comp-001", "company")
        for c in report.candidates:
            print(f"{c.candidate_name}: {c.future_alignment_score:.0%} aligned")
    """

    _instance: Optional["FutureConnectionEngine"] = None

    def __init__(self):
        self.registry = get_registry()
        self.context_engine = get_context_engine()
        self.possibility_engine = get_possibility_engine()
        self.future_registry = get_future_registry()
        self.decision_memory = DecisionMemory.get_instance()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Public API: Discover ----

    def discover_connections(self, node_id, node_type, extra_data=None):
        """Discover partner nodes that can help reach future states.

        Pipeline:
          1. Project the node's possibility graph
          2. Extract connection needs from future states
          3. Discover candidates that can fill those needs
          4. Score candidates using Future Alignment Score (5 factors)
          5. Return ranked candidates grouped by future state
        """
        # Step 1: Project possibilities
        graph = self.possibility_engine.project_from_data(
            node_id, node_type, extra_data or {})

        report = ConnectionReport(
            node_id=node_id,
            current_state=graph.current_state.description if graph.current_state else "",
        )

        # Get target future states (furthest horizon first)
        states_180 = graph.get_state_at_horizon(180)
        states_90 = graph.get_state_at_horizon(90)
        target_states = states_180 or states_90

        report.target_future_states = [
            f"{s.horizon_label}: {s.description}" for s in target_states[:3]
        ]

        if not target_states:
            report.summary = "Current node has no future state projections yet."
            return report

        # Step 2: Extract connection needs from possibility graph
        all_needs = graph.get_all_required_connections()
        for need_data in all_needs:
            need = ConnectionNeed(
                source_node_id=node_id,
                future_state_label=need_data.get("path", ""),
                needed_capability=need_data.get("type", ""),
                needed_node_type=need_data.get("type", "company"),
                urgency=need_data.get("urgency", "medium"),
                reason=need_data.get("reason", ""),
                current_gap_score=0.7 if need_data.get("urgency") == "high" else 0.4,
            )
            report.needs.append(need)

        # Step 3 & 4: Score candidates against each future state
        ctx = self.context_engine.understand(node_id, node_type, extra_data or {})
        candidate_pool = self._get_candidate_pool(node_id)

        for candidate_data in candidate_pool:
            if candidate_data["id"] == node_id:
                continue
            for target_state in target_states:
                alignment = self._calculate_alignment(
                    candidate_data, target_state, report.needs, ctx)
                if alignment.future_alignment_score > 0.2:
                    alignment.connected_future_state = target_state.description[:60]
                    report.candidates.append(alignment)

        # Deduplicate: keep highest score per candidate + future state pair
        seen = {}
        deduped = []
        for c in sorted(report.candidates,
                        key=lambda x: x.future_alignment_score, reverse=True):
            key = f"{c.candidate_node_id}:{c.connected_future_state[:30]}"
            if key not in seen:
                seen[key] = True
                deduped.append(c)
        report.candidates = deduped

        # Generate summary
        report.summary = self._generate_summary(report)
        return report

    def discover_for_company(self, company_id):
        """Convenience: discover connections for a company node."""
        return self.discover_connections(company_id, "company").to_dict()

    def discover_for_provider(self, provider_id):
        """Convenience: discover connections for a provider node."""
        return self.discover_connections(provider_id, "provider").to_dict()

    # ---- Public API: Record ----

    def record_connection(self, node_id, candidate_id, future_state, outcome_score=0.0):
        """Record that a connection was made and store initial outcome feedback."""
        rec = self.decision_memory.record_decision(
            node_id=node_id,
            decision_type="connection_made",
            chosen_path=f"Connected with {candidate_id} for {future_state}",
            expected=f"Advance towards {future_state}",
        )
        if outcome_score != 0:
            self.decision_memory.record_outcome(
                rec.record_id,
                f"Connection outcome for {future_state}",
                outcome_score,
            )
        return {
            "recorded": True,
            "record_id": rec.record_id,
            "outcome_score": outcome_score,
        }

    def get_connection_history(self, node_id):
        """Get recorded connection history for a node."""
        return self.decision_memory.get_history(node_id)

    # ---- Candidate Pool ----

    def _get_candidate_pool(self, exclude_id=""):
        """Get candidate nodes from the universe.

        In production this queries the database; currently uses a structured
        simulation pool that reflects real GEO ecosystem roles.
        """
        return [
            {"id": "data-corps-01", "type": "company",
             "name": "DataNova Technologies",
             "caps": ["data", "analysis", "observe"],
             "trust": 88, "influence": 75,
             "label": "Industry Data Analysis Leader"},
            {"id": "cert-org-01", "type": "provider",
             "name": "TrustCert Institute",
             "caps": ["certify", "verify", "observe"],
             "trust": 92, "influence": 82,
             "label": "Authoritative Certification Body"},
            {"id": "agent-lab-01", "type": "ai_agent",
             "name": "AgentForge AI",
             "caps": ["observe", "learn", "adapt", "recommend", "serve"],
             "trust": 78, "influence": 65,
             "label": "AI Agent R&D and Deployment Platform"},
            {"id": "gov-digital-01", "type": "government",
             "name": "Digital Economy Bureau",
             "caps": ["govern", "regulate", "observe", "certify"],
             "trust": 90, "influence": 95,
             "label": "Digital Economy Governance Body"},
            {"id": "content-pro-01", "type": "provider",
             "name": "ContentCraft Studio",
             "caps": ["build", "serve", "connect", "observe"],
             "trust": 72, "influence": 45,
             "label": "AI Content Production Expert"},
            {"id": "tech-platform-01", "type": "company",
             "name": "Nebula Tech Platform",
             "caps": ["build", "connect", "trade", "invest", "observe", "recommend"],
             "trust": 85, "influence": 88,
             "label": "Enterprise Tech Infrastructure Platform"},
            {"id": "edu-academy-01", "type": "company",
             "name": "GEO Academy",
             "caps": ["teach", "research", "report", "observe", "connect"],
             "trust": 80, "influence": 60,
             "label": "GEO Industry Education and Training"},
            {"id": "partner-group-01", "type": "company",
             "name": "EcoChain Partners",
             "caps": ["connect", "trade", "collaborate", "observe", "match"],
             "trust": 76, "influence": 70,
             "label": "Industry Ecosystem Connection Network"},
            {"id": "finance-firm-01", "type": "company",
             "name": "GrowthCap Ventures",
             "caps": ["invest", "finance", "evaluate", "observe"],
             "trust": 84, "influence": 78,
             "label": "Industry Investment and Financing Services"},
            {"id": "legal-firm-01", "type": "provider",
             "name": "ComplianceGuard Legal",
             "caps": ["verify", "govern", "regulate", "observe"],
             "trust": 91, "influence": 72,
             "label": "Compliance and Legal Support"},
        ]

    # ---- Scoring Engine ----

    def _calculate_alignment(self, candidate, target_state, needs, ctx):
        """Calculate the 5-factor Future Alignment Score.

        Weights:
          - Capability Complementarity: 0.35
          - Reputation Compatibility:  0.25
          - Historical Outcome:         0.15
          - Network Position:           0.15
          - Future Path Match:          0.10
        """
        # Factor 1: Capability Complementarity
        raw_caps = ctx.capability_state.get("acquired", [])
        node_caps = set(c.get("name", "") if isinstance(c, dict) else str(c) for c in raw_caps)
        candidate_caps = set(candidate["caps"])
        gap_fill = candidate_caps - node_caps
        needed_types = set(n.needed_node_type for n in needs)
        needs_match = 1.0 if candidate["type"] in needed_types else 0.6
        cap_complementarity = min(len(gap_fill) * 0.2 * needs_match, 1.0)
        if not gap_fill:
            cap_complementarity = 0.15

        # Factor 2: Reputation Compatibility (dynamic from Reputation Engine)
        try:
            from app.universe.reputation_engine import get_reputation_engine
            re = get_reputation_engine()
            profile = re.get_profile(candidate["id"])
            if profile and profile.status != "UNKNOWN":
                trust_compat = profile.overall_score / 100.0
            else:
                trust_compat = candidate.get("trust", 50) / 100.0  # fallback
        except Exception:
            trust_compat = candidate.get("trust", 50) / 100.0

        # Factor 3: Historical Outcome
        hist = self.decision_memory.get_success_rate(candidate["type"])
        hist_factor = max(hist, 0.3)

        # Factor 4: Network Position
        net_position = candidate.get("influence", 50) / 100.0

        # Factor 5: Future Path Match
        needed_caps = set(n.needed_capability for n in needs)
        cap_needs_match = len(candidate_caps & needed_caps) / max(len(needed_caps), 1)
        future_match = (1.0 if candidate["type"] in needed_types else 0.5 + cap_needs_match) / 2.0

        # Weighted aggregation
        alignment = (
            cap_complementarity * 0.35 +
            trust_compat * 0.25 +  # Reputation Compatibility
            hist_factor * 0.15 +
            net_position * 0.15 +
            future_match * 0.10
        )

        # Edge strength classification
        if alignment > 0.7:
            edge = "strong"
        elif alignment > 0.4:
            edge = "moderate"
        else:
            edge = "weak"

        return ConnectionCandidate(
            candidate_node_id=candidate["id"],
            candidate_node_type=candidate["type"],
            candidate_name=candidate["name"],
            candidate_label=candidate.get("label", ""),
            future_alignment_score=round(alignment, 2),
            capability_complementarity=round(cap_complementarity, 2),
            trust_compatibility=round(trust_compat, 2),
            historical_outcome_factor=round(hist_factor, 2),
            network_position_bonus=round(net_position, 2),
            edge_strength=edge,
            recommendation=f"Connect: {candidate['name']} - {candidate.get('label', '')}",
        )

    # ---- Summary Generation ----

    def _generate_summary(self, report):
        if not report.candidates:
            return "No candidates found matching future path needs."
        top = sorted(report.candidates,
                     key=lambda x: x.future_alignment_score, reverse=True)[0]
        by_type = {}
        for c in report.candidates:
            by_type.setdefault(c.candidate_node_type, 0)
            by_type[c.candidate_node_type] += 1

        # Count with reputation vs without
        with_rep = sum(1 for c in report.candidates if c.trust_compatibility > 0.5)
        type_parts = [f"{count} {t}" for t, count in sorted(by_type.items())]
        strong_count = sum(1 for c in report.candidates if c.edge_strength == "strong")
        return (
            f"Found {len(report.candidates)} future path connection candidates "
            f"({', '.join(type_parts)}). "
            f"{strong_count} strong, {with_rep} with rep-trust. "
            f"Best match: {top.candidate_name} "
            f"(alignment {top.future_alignment_score:.0%})."
        )


# ---- Singleton accessor ----

@lru_cache()
def get_connection_engine():
    return FutureConnectionEngine.get_instance()
