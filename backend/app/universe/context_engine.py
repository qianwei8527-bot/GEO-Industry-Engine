# GEO Universe Context Engine
# Phase C1: The missing middle layer between raw engines and AI Agents.
#
# Every Agent should query Context instead of raw databases.
# Context aggregates Identity + Position + Memory + Capability + Relationships
# into a single coherent understanding of any node.
#
# It answers: who, where, what happened, what can do, what will happen, what risks.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from functools import lru_cache

from app.universe.registry import get_registry
from app.universe.position_engine import get_position_engine
from app.universe.memory_engine import get_memory_engine
from app.universe.capability_engine import get_capability_registry
from app.universe.world_model import get_world_model


@dataclass
class NodeContext:
    """Complete contextual understanding of a single Universe node.
    
    This is the single source of truth for all Agents, Growth Engines,
    and Connection Engines. No direct database access needed.
    """
    node_id: str
    node_type: str
    computed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # 1. Identity: who is this node?
    identity: Dict[str, Any] = field(default_factory=dict)

    # 2. Current Position: where is this node now?
    current_position: Dict[str, Any] = field(default_factory=dict)

    # 3. Historical Memory: what happened to this node?
    historical_memory: Dict[str, Any] = field(default_factory=dict)

    # 4. Capability State: what can this node do, and how well?
    capability_state: Dict[str, Any] = field(default_factory=dict)

    # 5. Relationship Context: who is this node connected to?
    relationship_context: Dict[str, Any] = field(default_factory=dict)

    # 6. Industry Context: where does this node fit in the ecosystem?
    industry_context: Dict[str, Any] = field(default_factory=dict)

    # 7. Future Signals: what is emerging for this node?
    future_signals: Dict[str, Any] = field(default_factory=dict)

    # 8. Reputation Profile: how trustworthy is this node?
    reputation_profile: Dict[str, Any] = field(default_factory=dict)

    # 10. Risk Assessment: what could go wrong?
    risk_assessment: Dict[str, Any] = field(default_factory=dict)

    # 9. Recommended Direction: what should this node do next?
    recommended_direction: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "computed_at": self.computed_at,
            "summary": self._generate_summary(),
            "identity": self.identity,
            "current_position": self.current_position,
            "historical_memory": self.historical_memory,
            "capability_state": self.capability_state,
            "relationship_context": self.relationship_context,
            "industry_context": self.industry_context,
            "future_signals": self.future_signals,
            "risk_assessment": self.risk_assessment,
            "recommended_direction": self.recommended_direction,
        }

    def to_agent_context(self) -> str:
        """Generate a text context suitable for passing to AI Agents."""
        lines = [
            f"# Node Context: {self.identity.get('name', self.node_id)}",
            f"Type: {self.identity.get('type_label', self.node_type)}",
            f"",
            f"## Current Position",
        ]
        pos = self.current_position.get("position", {})
        if pos:
            if pos.get("industry_rank") is not None:
                lines.append(f"- Industry rank: top {pos['industry_rank']*100:.0f}%")
            if pos.get("reputation_level"):
                lines.append(f"- Reputation: {pos['reputation_level']}")
            if pos.get("growth_stage"):
                lines.append(f"- Growth stage: {pos['growth_stage']}")
            if pos.get("influence_score"):
                lines.append(f"- Influence: {pos['influence_score']}/100")

        lines.append(f"\n## Capabilities")
        caps = self.capability_state.get("acquired", [])
        lines.append(f"- Acquired: {len(caps)}")
        for c in caps[:5]:
            lines.append(f"  - {c.get('label', c.get('cap_id', ''))}")

        lines.append(f"\n## Memory")
        mem = self.historical_memory.get("layers", {})
        lines.append(f"- Facts: {mem.get('facts', {}).get('count', 0)}")
        lines.append(f"- Events: {mem.get('events', {}).get('count', 0)}")
        lines.append(f"- Stories: {mem.get('stories', {}).get('count', 0)}")

        lines.append(f"\n## Risks")
        for risk in self.risk_assessment.get("risks", [])[:3]:
            lines.append(f"- [{risk.get('severity', '')}] {risk.get('description', '')}")

        lines.append(f"\n## Recommended Direction")
        lines.append(self.recommended_direction.get("summary", ""))

        return "\n".join(lines)

    def _generate_summary(self) -> str:
        name = self.identity.get("name", self.node_id)
        stage = self.current_position.get("position", {}).get("growth_stage", "")
        rep = self.current_position.get("position", {}).get("reputation_level", "")
        caps = len(self.capability_state.get("acquired", []))
        return f"{name}: {stage} stage, {rep} reputation, {caps} capabilities"


class ContextEngine:
    """Aggregates all Universe engines to produce a complete NodeContext.

    This is the SINGLE entry point for all AI Agents.
    Instead of querying databases, Agents query Context.

    Usage:
        engine = ContextEngine.get_instance()
        ctx = engine.understand("comp-001", "company", extra_data={...})
        agent_context = ctx.to_agent_context()  # text for AI input
    """

    _instance: Optional["ContextEngine"] = None

    def __init__(self):
        self.registry = get_registry()
        self.position = get_position_engine()
        self.memory = get_memory_engine()
        self.capability = get_capability_registry()
        self.world_model = get_world_model()

    @classmethod
    def get_instance(cls) -> "ContextEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Public API ----

    def understand(self, node_id: str, node_type: str,
                   extra_data: Dict[str, Any] = None) -> NodeContext:
        """Generate complete contextual understanding of a node.

        Args:
            node_id: the node's unique ID
            node_type: must match a key in UniverseRegistry
            extra_data: optional additional data (from DB or external source)
                {name, description, industry_id, region, geo_score, trust_score,
                 evidence_count, relationship_count, capability_count,
                 certification_count, relationships_list, industry_name, ...}
        """
        data = extra_data or {}
        ctx = NodeContext(node_id=node_id, node_type=node_type)

        # 1. Identity
        ctx.identity = self._build_identity(node_id, node_type, data)

        # 2. Position
        ctx.current_position = self._build_position(node_id, node_type, data)

        # 3. Memory
        ctx.historical_memory = self._build_memory(node_id)

        # 4. Capability
        ctx.capability_state = self._build_capability(node_id, node_type, data)

        # 5. Relationships
        ctx.relationship_context = self._build_relationships(data)

        # 6. Industry
        ctx.industry_context = self._build_industry(node_type, data)

        # 7. Future Signals
        ctx.future_signals = self._build_future_signals(node_type, data)

        # 8. Risks
        ctx.risk_assessment = self._build_risks(ctx)

        # 9. Direction
        ctx.recommended_direction = self._build_direction(ctx)

        # 10. Reputation Profile (C5.1 Integration)
        try:
            from app.universe.reputation_engine import get_reputation_engine
            re = get_reputation_engine()
            exp = re.get_explanation(node_id)
            ctx.reputation_profile = exp.to_dict()
        except Exception:
            ctx.reputation_profile = {"overview": {"status": "UNKNOWN"}}

        return ctx

    # ---- Private Builders ----

    def _build_identity(self, node_id: str, node_type: str, data: Dict) -> Dict:
        meta = self.registry.get_node_type(node_type)
        return {
            "node_id": node_id,
            "node_type": node_type,
            "type_label": meta.label if meta else node_type,
            "type_icon": meta.icon if meta else "",
            "name": data.get("name", node_id[:8]),
            "description": data.get("description", ""),
            "industry_id": data.get("industry_id", ""),
            "region": data.get("region", ""),
            "layer": meta.layer if meta else 99,
        }

    def _build_position(self, node_id: str, node_type: str, data: Dict) -> Dict:
        try:
            report = self.position.compute(node_id, node_type, {
                "evidence_count": data.get("evidence_count", 0),
                "relationship_count": data.get("relationship_count", 0),
                "capability_count": data.get("capability_count", 0),
                "certification_count": data.get("certification_count", 0),
                "trust_score": data.get("trust_score", 0),
                "geo_score": data.get("geo_score", 0),
            })
            return report.to_dict()
        except Exception:
            return {"error": "Position computation failed", "position": {}}

    def _build_memory(self, node_id: str) -> Dict:
        try:
            return self.memory.get_timeline(node_id)
        except Exception:
            return {"layers": {"facts": {"count": 0}, "events": {"count": 0}, "stories": {"count": 0}}}

    def _build_capability(self, node_id: str, node_type: str, data: Dict) -> Dict:
        try:
            # Ensure defaults are granted
            has_caps = self.capability.get_node_capabilities(node_id)
            if not has_caps:
                self.capability.grant_defaults(node_id, node_type)

            tree = self.capability.get_skill_tree(node_id)
            return {
                "acquired": tree.get("acquired", []),
                "available": tree.get("available", []),
                "locked": tree.get("locked", []),
                "total_acquired": tree.get("total_acquired", 0),
                "total_available": tree.get("total_available", 0),
            }
        except Exception:
            return {"acquired": [], "available": [], "total_acquired": 0}

    def _build_relationships(self, data: Dict) -> Dict:
        relationships = data.get("relationships_list", [])
        return {
            "total": len(relationships),
            "by_type": self._group_by(relationships, "type"),
            "partners": [r for r in relationships if r.get("type") in ("partners_with", "??")],
            "competitors": [r for r in relationships if r.get("type") in ("competes_with", "??")],
            "network_size": len(relationships),
            "network_density": min(len(relationships) / 20.0, 1.0) if relationships else 0.0,
        }

    def _build_industry(self, node_type: str, data: Dict) -> Dict:
        industry_name = data.get("industry_name", "")
        return {
            "industry_name": industry_name or "????",
            "industry_id": data.get("industry_id", ""),
            "company_count_in_industry": data.get("company_count_in_industry", 0),
            "node_role": self._infer_industry_role(node_type, data),
        }

    def _build_future_signals(self, node_type: str, data: Dict) -> Dict:
        wm = self.world_model
        emerging = wm.get_emerging(min_confidence=0.2)
        recognized = wm.get_recognized()
        return {
            "emerging_concepts": [
                {"name": c.name, "category": c.category, "confidence": c.confidence}
                for c in emerging
            ],
            "recognized_concepts": [
                {"name": c.name, "category": c.category}
                for c in recognized
            ],
            "trend_signals": data.get("trend_signals", []),
        }

    def _build_risks(self, ctx: NodeContext) -> Dict:
        risks = []
        pos = ctx.current_position.get("position", {})

        # Reputation risk
        if pos.get("reputation_level") in ("D", "E"):
            risks.append({"severity": "high", "category": "trust",
                          "description": "Low reputation ? at risk of being filtered by AI recommendations",
                          "mitigation": "Increase verifiable evidence and obtain certifications"})

        # Stagnation risk
        if pos.get("growth_stage") in ("position", "selfknow"):
            risks.append({"severity": "medium", "category": "growth",
                          "description": "Early growth stage ? competitors may overtake",
                          "mitigation": "Focus on capability building and relationship expansion"})

        # Capability gap risk
        available = ctx.capability_state.get("available", [])
        if len(available) > 5 and ctx.capability_state.get("total_acquired", 0) < 4:
            risks.append({"severity": "medium", "category": "capability",
                          "description": f"Missing {len(available)} accessible capabilities ? capability gap widening",
                          "mitigation": f"Prioritize: {', '.join([c.get('label', '') for c in available[:3]])}"})

        # Network isolation risk
        rels = ctx.relationship_context.get("total", 0)
        if rels < 3:
            risks.append({"severity": "low", "category": "network",
                          "description": "Sparse connection network ? may miss partnership opportunities",
                          "mitigation": "Connect with 3+ providers or partners in the ecosystem"})

        # Evidence risk
        mem_facts = ctx.historical_memory.get("layers", {}).get("facts", {})
        if mem_facts.get("count", 0) < 5:
            risks.append({"severity": "low", "category": "evidence",
                          "description": "Low evidence footprint ? AI may lack sufficient data to cite this node",
                          "mitigation": "Publish case studies, obtain certifications, build public evidence"})

        return {
            "risk_count": len(risks),
            "overall_risk": "high" if any(r["severity"] == "high" for r in risks) else
                           "medium" if any(r["severity"] == "medium" for r in risks) else "low",
            "risks": risks,
        }

    def _build_direction(self, ctx: NodeContext) -> Dict:
        pos = ctx.current_position.get("position", {})
        stage = pos.get("growth_stage", "position")
        caps = ctx.capability_state.get("available", [])
        risks = ctx.risk_assessment.get("risks", [])

        directions = []

        # Based on growth stage
        stage_guidance = {
            "position": "Understand your industry landscape. Use Detection to benchmark your current standing.",
            "selfknow": "Identify your capability gaps. Compare with competitors to find your unique advantage.",
            "action": "Build evidence. Submit certifications, publish case studies, and form partnerships.",
            "provision": "Deepen capability mastery. Move from having capabilities to proving them with outcomes.",
            "accumulate": "Expand your influence. Broker connections between other nodes in the ecosystem.",
            "reputation": "Maintain leadership. Mentor emerging nodes and set industry standards.",
        }
        if stage in stage_guidance:
            directions.append(stage_guidance[stage])

        # Based on available capabilities
        if caps:
            next_caps = [c.get("label", c.get("cap_id", "")) for c in caps[:3]]
            directions.append(f"Next capabilities to acquire: {', '.join(next_caps)}")

        # Based on risks
        high_risks = [r for r in risks if r["severity"] == "high"]
        if high_risks:
            directions.append(f"Address high-priority risk: {high_risks[0]['description']}")

        # Based on position
        if pos.get("industry_rank") is not None and pos["industry_rank"] > 0.5:
            directions.append("Current industry position is below median. Prioritize reputation building.")
        elif pos.get("industry_rank") is not None and pos["industry_rank"] <= 0.1:
            directions.append("Top 10% in industry. Focus on thought leadership and ecosystem contribution.")

        return {
            "summary": " | ".join(directions[:3]),
            "detailed": directions,
            "suggested_stage": ctx.current_position.get("interpretation", {}).get("suggested_stage", stage),
        }

    # ---- Helpers ----

    def _group_by(self, items: List, key: str) -> Dict[str, int]:
        result = {}
        for item in items:
            val = item.get(key, "unknown") if isinstance(item, dict) else "unknown"
            result[val] = result.get(val, 0) + 1
        return result

    def _infer_industry_role(self, node_type: str, data: Dict) -> str:
        geo_score = data.get("geo_score", 0)
        trust = data.get("trust_score", 0)
        if geo_score > 80 and trust > 80:
            return "?????"
        elif geo_score > 50:
            return "?????"
        elif node_type in ("government",):
            return "??????"
        elif node_type in ("ai_agent",):
            return "??????"
        return "?????"


@lru_cache()
def get_context_engine() -> ContextEngine:
    return ContextEngine.get_instance()
