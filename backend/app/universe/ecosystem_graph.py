# GEO Universe Ecosystem Graph Engine
# C6.9: dynamic projection of world relationship structure.
#
# Layers:
#   Structure   - who exists and where
#   Relation    - who connects to whom
#   Causality   - why changes happened
#   Evolution   - how a node grew
#   Connection  - who should be connected next
#
# No Neo4j. This is a projection over existing engines + event data.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid

from app.universe.registry import get_registry
from app.universe.context_engine import get_context_engine
from app.universe.reputation_engine import get_reputation_engine
from app.universe.memory_engine import get_memory_engine
from app.universe.relationship_engine import get_relationship_engine
from app.universe.connection_engine import get_connection_engine


@dataclass
class GraphNode:
    node_id: str = ""
    node_type: str = ""
    label: str = ""
    layer: int = 99
    stage: str = ""
    reputation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "layer": self.layer,
            "stage": self.stage,
            "reputation": self.reputation,
        }


@dataclass
class GraphEdge:
    source: str = ""
    target: str = ""
    relation_type: str = ""
    direction: str = "bidirectional"
    stage: str = ""
    strength: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "direction": self.direction,
            "stage": self.stage,
            "strength": round(self.strength, 2),
        }


@dataclass
class EcosystemNodeReport:
    node_id: str = ""
    node_type: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    structure: Dict[str, Any] = field(default_factory=dict)
    relations: Dict[str, Any] = field(default_factory=dict)
    causality: Dict[str, Any] = field(default_factory=dict)
    evolution: Dict[str, Any] = field(default_factory=dict)
    next_connections: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "generated_at": self.generated_at,
            "structure": self.structure,
            "relations": self.relations,
            "causality": self.causality,
            "evolution": self.evolution,
            "next_connections": self.next_connections,
        }


class EcosystemGraphEngine:
    """Projects the ecosystem structure around a node from existing engines."""

    _instance: Optional["EcosystemGraphEngine"] = None

    def __init__(self):
        self.registry = get_registry()
        self.context = get_context_engine()
        self.reputation = get_reputation_engine()
        self.memory = get_memory_engine()
        self.relationship = get_relationship_engine()
        self.connection = get_connection_engine()

    @classmethod
    def get_instance(cls) -> "EcosystemGraphEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def explain(self, node_id: str, node_type: str = "company",
                extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Explain why a node is where it is in the ecosystem."""
        data = extra_data or {}
        ctx = self.context.understand(node_id, node_type, data)
        report = EcosystemNodeReport(
            node_id=node_id,
            node_type=node_type,
            structure=self._structure(ctx),
            relations=self._relations(node_id, ctx, data),
            causality=self._causality(node_id),
            evolution=self._evolution(node_id, ctx),
            next_connections=self._next_connections(node_id, node_type, data),
        )
        return report.to_dict()

    def project_graph(self, node_id: str, node_type: str = "company",
                      extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Project the ecosystem graph around one node."""
        report = self.explain(node_id, node_type, extra_data)
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []

        meta = self.registry.get_node_type(node_type)
        nodes[node_id] = GraphNode(
            node_id=node_id,
            node_type=node_type,
            label=report["structure"].get("identity", {}).get("name", node_id[:8]),
            layer=meta.layer if meta else 99,
            stage=report["structure"].get("position", {}).get("stage", ""),
            reputation=report["structure"].get("position", {}).get("reputation", ""),
        )

        for edge in report["relations"].get("edges", []):
            target = edge["target"]
            edges.append(GraphEdge(
                source=node_id,
                target=target,
                relation_type=edge["relation_type"],
                direction=edge.get("direction", "bidirectional"),
                stage=edge.get("stage", ""),
                strength=edge.get("strength", 0.0),
            ))
            if target not in nodes:
                nodes[target] = GraphNode(
                    node_id=target,
                    node_type="node",
                    label=target[:8],
                    stage=edge.get("stage", ""),
                )

        for candidate in report["next_connections"].get("candidates", []):
            cid = candidate.get("node_id", "")
            if not cid:
                continue
            edges.append(GraphEdge(
                source=node_id,
                target=cid,
                relation_type="should_connect",
                direction="out",
                stage="candidate",
                strength=candidate.get("future_alignment_score", 0.0),
            ))
            if cid not in nodes:
                nodes[cid] = GraphNode(
                    node_id=cid,
                    node_type=candidate.get("node_type", "company"),
                    label=candidate.get("name", cid[:8]),
                    reputation=candidate.get("label", ""),
                )

        return {
            "generated_at": report["generated_at"],
            "focal_node": node_id,
            "layers": {
                "structure": report["structure"],
                "relation": report["relations"],
                "causality": report["causality"],
                "evolution": report["evolution"],
                "connection": report["next_connections"],
            },
            "nodes": [n.to_dict() for n in nodes.values()],
            "edges": [e.to_dict() for e in edges],
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

    # ---- Layer builders ----

    def _structure(self, ctx) -> Dict[str, Any]:
        position = ctx.current_position.get("position", {})
        rep = ctx.reputation_profile.get("overview", {})
        return {
            "identity": ctx.identity,
            "position": {
                "industry": ctx.industry_context.get("industry_name", ""),
                "industry_id": ctx.industry_context.get("industry_id", ""),
                "stage": position.get("growth_stage", ""),
                "reputation": position.get("reputation_level") or rep.get("level", ""),
                "status": rep.get("status", "UNKNOWN"),
                "industry_rank": position.get("industry_rank"),
            },
            "capabilities": [
                c.get("label", c.get("cap_id", ""))
                for c in ctx.capability_state.get("acquired", [])
            ],
            "capability_count": ctx.capability_state.get("total_acquired", 0),
        }

    def _relations(self, node_id: str, ctx, data: Dict) -> Dict[str, Any]:
        edges = []
        seen = set()
        for rel in self.relationship.get_node_relationships(node_id):
            other = rel.node_b_id if rel.node_a_id == node_id else rel.node_a_id
            key = f"{other}:{rel.relationship_type}"
            if key in seen:
                continue
            seen.add(key)
            trust = (rel.relationship_trust or {}).get("overall", 0.0)
            edges.append({
                "target": other,
                "relation_type": rel.relationship_type,
                "stage": rel.stage,
                "strength": trust,
                "direction": "bidirectional",
            })
        for item in (data.get("relationships_list") or []):
            other = item.get("node_id") or item.get("target") or ""
            rtype = item.get("type", "unknown")
            key = f"{other}:{rtype}"
            if not other or key in seen:
                continue
            seen.add(key)
            edges.append({
                "target": other,
                "relation_type": rtype,
                "stage": item.get("stage", "CONNECTED"),
                "strength": item.get("strength", 0.0),
                "direction": item.get("direction", "bidirectional"),
            })
        by_type: Dict[str, int] = {}
        for e in edges:
            by_type[e["relation_type"]] = by_type.get(e["relation_type"], 0) + 1
        return {
            "total": len(edges),
            "by_type": by_type,
            "edges": edges,
        }

    def _causality(self, node_id: str) -> Dict[str, Any]:
        events = sorted(
            self.reputation.get_history(node_id),
            key=lambda e: e.get("timestamp", ""),
        )[-12:]
        if not events:
            return {
                "available": False,
                "chain": [],
                "explanation": "No reputation events yet; causality cannot be projected.",
            }
        labels = {
            "certification_passed": "认证通过，信任基础增强",
            "compliance_audit_passed": "合规审计通过，治理可信度上升",
            "customer_success": "客户成功形成可验证证据",
            "peer_endorsement": "伙伴背书扩大影响",
            "relationship_strengthened": "合作关系强化",
            "innovation_release": "创新成果发布",
            "industry_citation": "行业引用提升可见度",
            "ai_agent_cited": "AI 引用提升 GEO 可见度",
            "negative_feedback": "负面反馈形成风险",
        }
        chain = []
        for i, e in enumerate(events, start=1):
            chain.append({
                "step": i,
                "event_type": e.get("event_type", ""),
                "description": e.get("description", ""),
                "label": labels.get(e.get("event_type", ""), e.get("event_type", "")),
                "timestamp": (e.get("timestamp") or "")[:10],
                "impact": e.get("effective_weight", 0),
            })
        return {
            "available": True,
            "chain": chain,
            "explanation": "Causality projected from reputation event timeline.",
        }

    def _evolution(self, node_id: str, ctx) -> Dict[str, Any]:
        profile = self.reputation.get_profile(node_id)
        snap = profile.to_dict() if profile else {}
        history = self.reputation.get_history(node_id)
        rel_count = len(self.relationship.get_node_relationships(node_id))
        facts_count = ctx.historical_memory.get("layers", {}).get("facts", {}).get("count", 0)

        level = snap.get("overall_level", "")
        status = snap.get("status", "UNKNOWN")
        if level in ("A", "A+") or status in ("TRUSTED", "ESTABLISHED"):
            stage = "trusted"
        elif level in ("B", "C") or status in ("ACTIVE", "VERIFIED"):
            stage = "active"
        else:
            stage = "entry"

        milestones = [
            {
                "date": (e.get("timestamp") or "")[:10],
                "event": e.get("description", e.get("event_type", "")),
                "impact": e.get("effective_weight", 0),
            }
            for e in history[-6:]
        ]
        return {
            "current_stage": stage,
            "reputation_level": level or "N/A",
            "reputation_status": status,
            "reputation_trend": snap.get("trend", "stable"),
            "evidence_count": max(len(history), facts_count),
            "relationship_count": rel_count,
            "milestones": milestones,
        }

    def _next_connections(self, node_id: str, node_type: str,
                          data: Dict) -> Dict[str, Any]:
        try:
            return self.connection.discover_connections(node_id, node_type, data).to_dict()
        except Exception:
            return {
                "node_id": node_id,
                "needs": [],
                "candidates": [],
                "candidate_count": 0,
                "summary": "Connection projection unavailable.",
            }


def get_ecosystem_graph_engine() -> EcosystemGraphEngine:
    return EcosystemGraphEngine.get_instance()
