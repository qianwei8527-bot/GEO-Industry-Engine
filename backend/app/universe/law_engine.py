"""C6.7 Universe Law Governance Layer.

Four capabilities:
  A. Law Registry     — laws as governed Universe Entities (id/version/status/owner/audit)
  B. Law Evaluation   — Event -> Law Candidate -> Condition -> Mutation Plan -> Execute
  C. Law Conflict     — priority resolution; risk overrides growth
  D. Law Explanation  — every mutation explains WHY (event/law/evidence/impact/confidence)
"""
import os
from typing import Dict, List, Optional, Any
from functools import lru_cache
import yaml

from app.universe.event_backbone import UniverseEvent, get_event_backbone

_LAWS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                          'config', 'universe', 'laws.yaml')


# ── A. Law Registry ──

class LawRegistry:
    def __init__(self, path=None):
        self.path = path or _LAWS_PATH
        self.laws: List[Dict] = []
        self.reload()

    def reload(self):
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as f:
                self.laws = (yaml.safe_load(f) or {}).get("laws", [])

    def get(self, law_id: str) -> Optional[Dict]:
        for law in self.laws:
            if law.get("law_id") == law_id:
                return law
        return None

    def candidates(self, event: UniverseEvent) -> List[Dict]:
        """All laws whose trigger matches this event, sorted by priority desc."""
        out = []
        for law in self.laws:
            if law.get("status") != "active":
                continue
            triggers = law.get("trigger", {}).get("event_type", [])
            et = event.event_type
            if et in triggers or f"{event.domain}.{et}" in triggers:
                out.append(law)
        out.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return out


# ── B. Condition Evaluation ──

class ConditionEvaluator:
    def evaluate(self, law: Dict, event: UniverseEvent, context: Dict) -> bool:
        cond = law.get("conditions", {}) or {}
        # evidence_status.equals: str or list
        es = cond.get("evidence_status", {}).get("equals")
        if es is not None:
            actual = context.get("evidence_status", "observed")
            allowed = es if isinstance(es, list) else [es]
            if actual not in allowed:
                return False
        # source_type.equals
        st = cond.get("source_type", {}).get("equals")
        if st is not None and event.source != st:
            return False
        # min_evidence
        me = cond.get("min_evidence")
        if me is not None and context.get("evidence_count", 0) < me:
            return False
        # reputation_risk.less_than
        rr = cond.get("reputation_risk", {}).get("less_than")
        if rr is not None and context.get("reputation_risk", 0) >= rr:
            return False
        return True


# ── C. Conflict Resolver ──

class ConflictResolver:
    RISK_THRESHOLD = 100

    def resolve(self, candidates: List[Dict]) -> Dict:
        """Pick applicable laws with conflict policy:
        - highest priority wins per dimension
        - risk laws (priority>=100) always override growth laws
        Returns final laws + suppressed laws with reasons.
        """
        if not candidates:
            return {"applied": [], "suppressed": []}
        winners, suppressed = [], []
        for law in candidates:
            # growth laws suppressed when a risk law applies
            if law.get("priority", 0) < self.RISK_THRESHOLD:
                has_risk = any(l.get("priority", 0) >= self.RISK_THRESHOLD for l in candidates)
                if has_risk:
                    suppressed.append({"law_id": law.get("law_id"),
                                       "reason": "risk_law_override"})
                    continue
            winners.append(law)
        return {"applied": winners, "suppressed": suppressed}


# ── D. Explanation ──

class LawExplanation:
    def build(self, event: UniverseEvent, law: Dict, context: Dict, applied: List[Dict],
              confidence: float) -> Dict:
        return {
            "event": {"event_id": event.event_id, "type": event.event_type,
                      "actor": event.actor_id, "occurred_at": event.occurred_at},
            "law": {"law_id": law.get("law_id"), "version": law.get("version"),
                    "status": law.get("status"), "owner": law.get("owner")},
            "conditions_met": {k: v for k, v in context.items() if k in ("evidence_status", "source_type")},
            "impacts": applied,
            "confidence": confidence,
            "principle": "Law is governance, not creation.",
        }


# ── Engine ──

class UniverseLawEngine:
    _instance = None

    def __init__(self):
        self.registry = LawRegistry()
        self.conditions = ConditionEvaluator()
        self.conflicts = ConflictResolver()
        self.explanation = LawExplanation()

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    async def handle(self, event: UniverseEvent, context: Dict = None) -> Dict:
        backbone = get_event_backbone()
        backbone.emit(event)
        context = context or {}
        candidates = self.registry.candidates(event)
        if not candidates:
            return {"event_id": event.event_id, "matched": False,
                    "applied_laws": [], "suppressed": [], "mutations": [],
                    "explanation": None}

        applicable = [law for law in candidates if self.conditions.evaluate(law, event, context)]
        resolution = self.conflicts.resolve(applicable)
        mutations = []
        for law in resolution["applied"]:
            event.rule_ids.append(law.get("law_id"))
            effects = await self._apply(event, law, context)
            mutations.append(effects)
        return {
            "event_id": event.event_id,
            "matched": True,
            "correlation_id": event.correlation_id,
            "applied_laws": [l.get("law_id") for l in resolution["applied"]],
            "suppressed": resolution["suppressed"],
            "mutations": mutations,
            "explanation": [self.explanation.build(event, law, context, m.get("applied", []), 0.8)
                            for law, m in zip(resolution["applied"], mutations)],
        }

    async def _apply(self, event: UniverseEvent, law: Dict, context: Dict) -> Dict:
        effects = law.get("effects", {})
        applied = []
        for rep in effects.get("reputation", []):
            try:
                from app.universe.reputation_engine import get_reputation_engine
                re = get_reputation_engine()
                re.record_event(event.node_id, "company", rep.get("event_type", "capability_verified"),
                                f"Law {law['law_id']} v{law.get('version')}: {event.event_type}",
                                rep.get("source", "government"))
                re.recalculate(event.node_id, "company")
                applied.append({"engine": "reputation", "dimension": rep.get("dimension"),
                                "delta": rep.get("delta")})
            except Exception as e:
                applied.append({"engine": "reputation", "error": str(e)[:120]})
        if effects.get("position", {}).get("recompute"):
            try:
                from app.universe.context_engine import get_context_engine
                ctx = get_context_engine().understand(event.node_id, "company", {})
                applied.append({"engine": "position",
                                "growth_stage": ctx.current_position.get("position", {}).get("growth_stage")})
            except Exception as e:
                applied.append({"engine": "position", "error": str(e)[:120]})
        story = effects.get("memory", {}).get("story")
        if story:
            try:
                from app.universe.memory_engine import get_memory_engine
                mem = get_memory_engine()
                mem.record_fact(node_id=event.node_id, node_type="company", statement=story,
                                category="law", source=f"law:{law['law_id']}")
                applied.append({"engine": "memory", "story": story})
            except Exception as e:
                applied.append({"engine": "memory", "error": str(e)[:120]})
        return {"law_id": law.get("law_id"), "version": law.get("version"), "applied": applied}

    @classmethod
    def reset(cls):
        cls._instance = None
        get_event_backbone().reset()


@lru_cache()
def get_law_engine():
    return UniverseLawEngine.get_instance()
