# GEO Universe Possibility Graph Engine
# Phase C3: From "5 recommendations" to "future state evolution space".
#
# The Possibility Engine takes current node state and projects a graph of
# possible future states at 30/90/180 day horizons. Each path unfolds into
# a sequence of transitions with probability, conditions, benefits, risks,
# and required connections.
#
# Principle: Connection exists to enter shared future paths together.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from functools import lru_cache
import uuid
import math

from app.universe.registry import get_registry
from app.universe.context_engine import NodeContext, get_context_engine
from app.universe.decision_engine import DecisionEngine, CandidatePath, get_decision_engine
from app.universe.future_registry import FutureStateRegistry, get_future_registry


@dataclass
class FutureState:
    """A single possible future state of a node at a specific horizon."""
    state_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    horizon_label: str = ""            # "??" | "30?" | "90?" | "180?"
    horizon_days: int = 0
    stage: str = ""                    # growth stage
    reputation: str = ""               # A-E
    influence: float = 0.0             # 0-100
    capability_count: int = 0
    relationship_count: int = 0
    evidence_count: int = 0
    new_capabilities: List[str] = field(default_factory=list)
    new_connections: List[str] = field(default_factory=list)  # required partner types
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "horizon": self.horizon_label,
            "horizon_days": self.horizon_days,
            "stage": self.stage,
            "reputation": self.reputation,
            "influence": self.influence,
            "capability_count": self.capability_count,
            "relationship_count": self.relationship_count,
            "evidence_count": self.evidence_count,
            "new_capabilities": self.new_capabilities,
            "new_connections": self.new_connections,
            "description": self.description,
        }


@dataclass
class Transition:
    """A transition from current state to a future state along a path."""
    transition_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    from_state: str = ""               # state_id of source
    to_state: str = ""                 # state_id of target
    path_title: str = ""               # which decision path this belongs to
    probability: float = 0.0           # 0-1 likelihood of reaching this state
    conditions: List[str] = field(default_factory=list)     # what must be true
    benefits: List[str] = field(default_factory=list)       # what you gain
    risks: List[Dict] = field(default_factory=list)         # what could go wrong
    required_connections: List[Dict] = field(default_factory=list)  # [{type, reason}]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "from": self.from_state,
            "to": self.to_state,
            "path": self.path_title,
            "probability": round(self.probability, 2),
            "conditions": self.conditions,
            "benefits": self.benefits,
            "risks": self.risks,
            "required_connections": self.required_connections,
        }


@dataclass
class DecisionMemoryRecord:
    """A record of a decision made by a node and its outcome."""
    record_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_id: str = ""
    decision_type: str = ""            # path_chosen | connection_made | capability_acquired
    proposed_at: str = ""
    chosen_path: str = ""
    expected_outcome: str = ""
    actual_outcome: str = ""
    outcome_score: float = 0.0         # -1 to 1 (negative = worse than expected)
    feedback_notes: str = ""
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "node_id": self.node_id,
            "decision_type": self.decision_type,
            "chosen_path": self.chosen_path,
            "expected_outcome": self.expected_outcome,
            "actual_outcome": self.actual_outcome,
            "outcome_score": self.outcome_score,
        }


class PossibilityGraph:
    """The complete graph of possible futures for a node.

    Contains all FutureStates and Transitions, forming a directed acyclic
    graph from the present outward. Paths can converge and diverge.
    """

    def __init__(self, node_id: str, node_type: str):
        self.node_id = node_id
        self.node_type = node_type
        self.current_state: Optional[FutureState] = None
        self.states: Dict[str, FutureState] = {}
        self.transitions: List[Transition] = []
        self.convergence_points: List[str] = []  # state_ids where multiple paths meet
        self.divergence_points: List[str] = []   # state_ids where paths split
        self.generated_at: str = datetime.now(timezone.utc).isoformat()
        self.horizon_availability: Dict[str, Any] = {}

    def add_state(self, state: FutureState):
        self.states[state.state_id] = state

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)

    def mark_convergence(self, state_id: str):
        """Mark a state as a convergence point (multiple paths lead here)."""
        self.convergence_points.append(state_id)

    def mark_divergence(self, state_id: str):
        """Mark a state as a divergence point (paths split from here)."""
        self.divergence_points.append(state_id)

    def get_path_sequence(self, path_title: str) -> List[Tuple[FutureState, Transition]]:
        """Get the full state+transition sequence for a specific path."""
        seq = []
        trans = [t for t in self.transitions if t.path_title == path_title]
        for t in sorted(trans, key=lambda x: self.states.get(x.to_state, FutureState()).horizon_days):
            to_state = self.states.get(t.to_state)
            if to_state:
                seq.append((to_state, t))
        return seq

    def get_state_at_horizon(self, horizon_days: int) -> List[FutureState]:
        """Get all reachable future states at a specific horizon."""
        return [s for s in self.states.values() if s.horizon_days == horizon_days]

    def get_all_required_connections(self) -> List[Dict]:
        """Collect all connection needs across all transitions."""
        connections = []
        for t in self.transitions:
            for conn in t.required_connections:
                connections.append({
                    "path": t.path_title,
                    "transition": t.transition_id,
                    **conn,
                })
        return connections

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "generated_at": self.generated_at,
            "current_state": self.current_state.to_dict() if self.current_state else None,
            "states": {sid: s.to_dict() for sid, s in self.states.items()},
            "transitions": [t.to_dict() for t in self.transitions],
            "convergence_points": self.convergence_points,
            "divergence_points": self.divergence_points,
            "connection_needs": self.get_all_required_connections(),
            "horizon_availability": self.horizon_availability,
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> str:
        states_30 = self.get_state_at_horizon(30)
        states_90 = self.get_state_at_horizon(90)
        states_180 = self.get_state_at_horizon(180)
        return (
            f"??? {len(self.states)} ??????"
            f"30? {len(states_30)} ??90? {len(states_90)} ??180? {len(states_180)} ??"
            f"??????? {len(self.get_all_required_connections())} ??"
        )


class DecisionMemory:
    """Persistent memory of all decisions made and their outcomes.

    This feeds back into the Decision Engine to improve future path scoring.
    Nodes with good decision outcomes boost the probability of similar paths
    for other nodes in similar positions.
    """

    _instance: Optional["DecisionMemory"] = None

    def __init__(self):
        self.records: List[DecisionMemoryRecord] = []

    @classmethod
    def get_instance(cls) -> "DecisionMemory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def record_decision(self, node_id: str, decision_type: str,
                        chosen_path: str, expected: str) -> DecisionMemoryRecord:
        rec = DecisionMemoryRecord(
            node_id=node_id,
            decision_type=decision_type,
            proposed_at=datetime.now(timezone.utc).isoformat(),
            chosen_path=chosen_path,
            expected_outcome=expected,
        )
        self.records.append(rec)
        return rec

    def record_outcome(self, record_id: str, actual_outcome: str,
                       outcome_score: float, notes: str = "") -> Optional[DecisionMemoryRecord]:
        for rec in self.records:
            if rec.record_id == record_id:
                rec.actual_outcome = actual_outcome
                rec.outcome_score = outcome_score
                rec.feedback_notes = notes
                return rec
        return None

    def get_success_rate(self, path_category: str) -> float:
        """Get the success rate for a category of decisions."""
        relevant = [r for r in self.records if r.chosen_path and path_category in r.chosen_path and r.outcome_score != 0]
        if not relevant:
            return 0.5
        positive = sum(1 for r in relevant if r.outcome_score > 0)
        return positive / len(relevant)

    def get_node_history(self, node_id: str) -> List[DecisionMemoryRecord]:
        return [r for r in self.records if r.node_id == node_id]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records": len(self.records),
            "pending_outcomes": sum(1 for r in self.records if r.outcome_score == 0),
            "avg_outcome_score": round(
                sum(r.outcome_score for r in self.records if r.outcome_score != 0) /
                max(1, sum(1 for r in self.records if r.outcome_score != 0)), 2
            ),
        }


class PossibilityEngine:
    """Projects node current state into a graph of possible futures.

    Usage:
        engine = PossibilityEngine.get_instance()
        ctx = context_engine.understand(...)
        graph = engine.project(ctx)
        for state in graph.get_state_at_horizon(90):
            print(f"90 days: {state.description}")
    """

    _instance: Optional["PossibilityEngine"] = None

    # Stage evolution now managed by FutureStateRegistry (config/universe/futures.yaml)
    # No hardcoded progression tables. All future states are configurable.

    def __init__(self):
        self.registry = get_registry()
        self.context_engine = get_context_engine()
        self.decision_engine = get_decision_engine()
        self.decision_memory = DecisionMemory.get_instance()
        self.future_registry = get_future_registry()

    @classmethod
    def get_instance(cls) -> "PossibilityEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Public API ----

    def project(self, ctx: NodeContext) -> PossibilityGraph:
        """Project a node's current state into a graph of possible futures.

        Returns a PossibilityGraph with states at 30/90/180 day horizons,
        transitions between states, and required connections for each path.
        """
        graph = PossibilityGraph(ctx.node_id, ctx.node_type)

        # Build current state
        pos = ctx.current_position.get("position", {})
        current = FutureState(
            state_id="current",
            horizon_label="??",
            horizon_days=0,
            stage=pos.get("growth_stage", "position"),
            reputation=pos.get("reputation_level", "C"),
            influence=pos.get("influence_score", 0),
            capability_count=ctx.capability_state.get("total_acquired", 0),
            relationship_count=ctx.relationship_context.get("total", 0),
            evidence_count=ctx.historical_memory.get("layers", {}).get("facts", {}).get("count", 0),
            description=f"???{ctx._generate_summary()}",
        )
        graph.current_state = current
        graph.add_state(current)

        # C6.1 Gate 0-5: horizons come from learning.yaml (30/90/180).
        try:
            import os as _os, yaml as _yaml
            _p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                               'config', 'universe', 'learning.yaml')
            _cfg = _yaml.safe_load(open(_p, encoding='utf-8')) if _os.path.exists(_p) else {}
            self.horizons = [h['days'] for h in _cfg.get('possibility_horizons', [])]
            self.horizon_unavailable_reason = _cfg.get('possibility_unavailable_reason', '当前数据不足，无法生成该时间窗推演')
        except Exception:
            self.horizons = [30, 90, 180]
            self.horizon_unavailable_reason = '当前数据不足，无法生成该时间窗推演'

        # Get decision paths from Decision Engine
        report = self.decision_engine.decide(ctx)
        paths = report.paths[:4]  # Top 4 paths

        # For each path, project a sequence of future states
        for i, path in enumerate(paths):
            self._project_path(graph, current, path, i + 1)

        # Detect convergence and divergence
        self._detect_convergence_divergence(graph)

        # Availability: mark each configured horizon as available or unavailable
        available = {s.horizon_days for s in graph.states.values() if s.horizon_days > 0}
        graph.horizon_availability = {}
        for h in getattr(self, 'horizons', [30, 90, 180]):
            if h in available:
                graph.horizon_availability[str(h)] = {"available": True, "states": sum(1 for s in graph.states.values() if s.horizon_days == h)}
            else:
                graph.horizon_availability[str(h)] = {"available": False, "reason": getattr(self, 'horizon_unavailable_reason', '')}

        return graph

    def project_from_data(self, node_id: str, node_type: str,
                          extra_data: Dict = None) -> PossibilityGraph:
        ctx = self.context_engine.understand(node_id, node_type, extra_data or {})
        return self.project(ctx)

    def record_decision(self, node_id: str, path_title: str,
                        decision_type: str = "path_chosen") -> DecisionMemoryRecord:
        """Record that a node chose a specific path."""
        return self.decision_memory.record_decision(
            node_id=node_id,
            decision_type=decision_type,
            chosen_path=path_title,
            expected=f"Follow path: {path_title}",
        )

    def record_outcome(self, record_id: str, actual: str, score: float) -> Optional[DecisionMemoryRecord]:
        """Record the actual outcome of a decision."""
        return self.decision_memory.record_outcome(record_id, actual, score)

    # ---- Path Projection ----

    def _project_path(self, graph: PossibilityGraph, current: FutureState,
                      path: CandidatePath, path_idx: int):
        """Project one decision path into a sequence of future states."""
        horizons = getattr(self, 'horizons', [30, 90, 180])
        max_horizon = min(path.timeframe_days, max(horizons))
        applicable_horizons = [h for h in horizons if h <= max_horizon]

        prev_state = current
        for horizon in applicable_horizons:
            progress = horizon / max(path.timeframe_days, 1)
            prob = path.suitability_score * (1.0 - progress * 0.3)  # Probability decays over time

            # Create future state
            future = self._build_future_state(
                prev_state, path, horizon, progress,
                f"{current.state_id}_path{path_idx}_{horizon}d",
                graph.node_type
            )
            graph.add_state(future)

            # Create transition
            transition = Transition(
                from_state=prev_state.state_id,
                to_state=future.state_id,
                path_title=path.title,
                probability=prob,
                conditions=self._build_conditions(path, progress),
                benefits=self._build_benefits(path, progress, future),
                risks=self._build_risks(path, progress),
                required_connections=self._build_connection_needs(path, progress, future),
            )
            graph.add_transition(transition)

            prev_state = future

    def _build_future_state(self, prev: FutureState, path: CandidatePath,
                            horizon: int, progress: float, state_id: str,
                            node_type: str = "company") -> FutureState:
        """Build a projected future state based on path progress."""
        # Stage progression ? now from FutureStateRegistry, not hardcoded
        current_stage = prev.stage
        next_stage = current_stage
        rep_next = prev.reputation

        # Query the FutureStateRegistry for reachable states
        template = self.future_registry.get_next(
            node_type, current_stage,
            capability_count=prev.capability_count,
            evidence_count=prev.evidence_count,
            relationship_count=prev.relationship_count,
            influence=prev.influence,
            reputation=prev.reputation,
        )
        if template:
            if progress > 0.3:
                next_stage = template.stage
            if progress > 0.7:
                rep_next = template.reputation_min if template.reputation_min else rep_next

        # Influence growth
        influence_gain = path.suitability_score * 15 * progress
        new_influence = min(prev.influence + influence_gain, 100)

        # Capability growth
        cap_gain = min(int(path.suitability_score * 3 * progress), len(path.required_capabilities))
        new_caps = path.required_capabilities[:cap_gain]

        # Relationship growth
        rel_gain = int(path.suitability_score * 5 * progress)

        descriptions = {
            30: f"30????????{path.title}?????????????",
            90: f"90???{path.title}????????????????",
            180: f"180???{path.title}????????????",
        }

        return FutureState(
            state_id=state_id,
            horizon_label=f"{horizon}?",
            horizon_days=horizon,
            stage=next_stage,
            reputation=rep_next,
            influence=round(new_influence, 1),
            capability_count=prev.capability_count + len(new_caps),
            relationship_count=prev.relationship_count + rel_gain,
            evidence_count=prev.evidence_count + int(progress * 10),
            new_capabilities=new_caps,
            new_connections=self._connection_types_for_path(path),
            description=descriptions.get(horizon, f"??{path.title}"),
        )

    def _build_conditions(self, path: CandidatePath, progress: float) -> List[str]:
        conditions = list(path.prerequisites)
        if progress < 0.5:
            conditions.append("????????")
        else:
            conditions.append("????????")
        return conditions

    def _build_benefits(self, path: CandidatePath, progress: float,
                        future: FutureState) -> List[str]:
        benefits = list(path.expected_outcomes[:2])
        if future.stage != progress and progress > 0.5:
            benefits.append(f"??????? {future.stage}")
        if future.reputation != "N/A":
            benefits.append(f"????? {future.reputation} ?")
        return benefits

    def _build_risks(self, path: CandidatePath, progress: float) -> List[Dict]:
        risks = list(path.risks[:2])
        if progress > 0.5:
            risks.append({"severity": "medium", "description": "????????????"})
        return risks

    def _build_connection_needs(self, path: CandidatePath, progress: float,
                                future: FutureState) -> List[Dict]:
        """Identify what types of connections this node needs at this stage."""
        needs = []
        if path.category == "capability":
            needs.append({
                "type": "provider",
                "reason": f"???? {path.required_capabilities[0] if path.required_capabilities else '??'} ??????",
                "urgency": "high" if progress < 0.3 else "medium",
            })
        if path.category == "partnership":
            needs.append({
                "type": "company",
                "reason": "????????????",
                "urgency": "high",
            })
        if path.category == "market":
            needs.append({
                "type": "industry",
                "reason": "???????????????",
                "urgency": "high" if progress < 0.3 else "medium",
            })
            needs.append({
                "type": "government",
                "reason": "?????????????",
                "urgency": "medium",
            })
        if path.category == "certification":
            needs.append({
                "type": "provider",
                "reason": "????????????",
                "urgency": "high",
            })
        if progress > 0.5:
            needs.append({
                "type": "company",
                "reason": "??????????????",
                "urgency": "medium",
            })
        return needs if needs else [
            {"type": "company", "reason": "?????????????", "urgency": "low"},
        ]

    def _connection_types_for_path(self, path: CandidatePath) -> List[str]:
        """Simple list of connection types needed for a path."""
        types = set()
        if path.category in ("capability", "certification"):
            types.add("provider")
        if path.category in ("partnership", "market"):
            types.add("company")
            types.add("industry")
        return list(types) if types else ["company"]

    # ---- Convergence / Divergence Detection ----

    def _detect_convergence_divergence(self, graph: PossibilityGraph):
        """Find convergence and divergence points in the possibility graph."""
        # States that have multiple incoming transitions = convergence
        incoming = {}
        for t in graph.transitions:
            incoming.setdefault(t.to_state, []).append(t.from_state)

        for state_id, sources in incoming.items():
            if len(sources) >= 2:
                graph.mark_convergence(state_id)

        # States that have multiple outgoing transitions = divergence
        outgoing = {}
        for t in graph.transitions:
            outgoing.setdefault(t.from_state, []).append(t.to_state)

        for state_id, targets in outgoing.items():
            if len(targets) >= 2:
                graph.mark_divergence(state_id)


@lru_cache()
def get_possibility_engine() -> PossibilityEngine:
    return PossibilityEngine.get_instance()
