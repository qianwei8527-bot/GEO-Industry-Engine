# GEO Universe Relationship Intelligence Engine
# Phase C5.3 - From Connection Candidate to Relationship Opportunity.
#
# C4: "Who could you connect with?"
# C5.1: "Who is trustworthy?"
# C5.2: "How does a relationship grow?"
# C5.3: "WHY should this connection happen?"
#
# Fuses: C4 + C5.1 + C5.2 + Possibility Graph + Context Engine
# Output: RelationshipOpportunity - comprehensive evaluation of
# WHY two nodes should connect, what value, what risks.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from functools import lru_cache
import uuid

from app.universe.context_engine import NodeContext, get_context_engine

print("Phase C5.3: Relationship Intelligence Engine loaded")

# ========== Data Models ==========

@dataclass
class RiskSignal:
    category: str = ""
    severity: str = "low"
    description: str = ""
    mitigation: str = ""
    def to_dict(self):
        return {"category":self.category,"severity":self.severity,"description":self.description,"mitigation":self.mitigation}

@dataclass
class NextStep:
    action: str = ""
    rationale: str = ""
    timeframe: str = ""
    expected_outcome: str = ""
    def to_dict(self):
        return {"action":self.action,"rationale":self.rationale,"timeframe":self.timeframe,"expected_outcome":self.expected_outcome}

@dataclass
class RelationshipOpportunity:
    opportunity_id: str = ""
    node_a_id: str = ""
    node_b_id: str = ""
    node_a_name: str = ""
    node_b_name: str = ""
    generated_at: str = ""
    reasons: Dict[str, Any] = field(default_factory=dict)
    existing_relationship: Dict[str, Any] = field(default_factory=dict)
    expected_value: Dict[str, Any] = field(default_factory=dict)
    risks: List[RiskSignal] = field(default_factory=list)
    next_steps: List[NextStep] = field(default_factory=list)
    recommended_action: str = ""
    confidence: float = 0.0
    connection_value: Dict[str, Any] = field(default_factory=dict)
    opportunity_event_id: str = "" 

    def __post_init__(self):
        if not self.opportunity_id: self.opportunity_id = str(uuid.uuid4())[:8]
        if not self.generated_at: self.generated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "opportunity_id":self.opportunity_id,"node_a_id":self.node_a_id,"node_b_id":self.node_b_id,
            "node_a_name":self.node_a_name,"node_b_name":self.node_b_name,"generated_at":self.generated_at,
            "reasons":self.reasons,
            "existing_relationship":self.existing_relationship,
            "expected_value":{k:round(v,2) if isinstance(v,float) else v for k,v in self.expected_value.items()},
            "risks":[r.to_dict() for r in self.risks],
            "next_steps":[s.to_dict() for s in self.next_steps],
            "recommended_action":self.recommended_action,
            "confidence":round(self.confidence,2),
            "connection_value":self.connection_value,
            "opportunity_event_id":self.opportunity_event_id,
        }

# ========== Opportunity Evaluator ==========

class OpportunityEvaluator:
    CAPABILITY_COMPLEMENTARITY_W = 0.30
    FUTURE_PATH_ALIGNMENT_W = 0.20
    REPUTATION_COMPATIBILITY_W = 0.20
    RELATIONSHIP_HISTORY_W = 0.15
    STRATEGIC_VALUE_W = 0.15

    def evaluate(self, node_a_id, node_b_id, node_a_name="", node_b_name="", node_a_type="company", node_b_type="company"):
        opp = RelationshipOpportunity(node_a_id=node_a_id, node_b_id=node_b_id, node_a_name=node_a_name or node_a_id, node_b_name=node_b_name or node_b_id)
        ctx_a = self._get_context(node_a_id, node_a_type)
        ctx_b = self._get_context(node_b_id, node_b_type)
        opp.reasons["capability_gap"] = self._calc_capability_gap(ctx_a, ctx_b)
        opp.reasons["future_alignment"] = self._calc_future_alignment(node_a_id, ctx_a)
        opp.reasons["reputation_match"] = self._calc_reputation_match(node_a_id, node_b_id)
        opp.existing_relationship = self._check_existing_relationship(node_a_id, node_b_id)
        opp.expected_value = self._calc_expected_value(opp.reasons)
        opp.risks = self._detect_risks(opp, ctx_b)
        opp.next_steps = self._generate_next_steps(opp)
        opp.confidence = self._calc_opportunity_score(opp)
        opp.recommended_action = self._generate_recommendation(opp)
        opp.connection_value = self._calc_connection_value(opp).to_dict()
        opp.opportunity_event_id = self._record_opportunity_created(opp)
        return opp

    def _get_context(self, node_id, node_type):
        try:
            return get_context_engine().get_context(node_id, node_type)
        except Exception:
            return None

    def _calc_capability_gap(self, ctx_a, ctx_b):
        gaps = []
        if not ctx_a or not ctx_b:
            return gaps
        b_caps = {}
        for c in ctx_b.capability_state.get("acquired", []):
            cap_id = c.get("cap_id") or c.get("name", "")
            b_caps[cap_id] = {"level": c.get("level", "Lv1"), "label": c.get("label", cap_id)}
        for c in ctx_a.capability_state.get("available", [])[:5]:
            cap_id = c.get("cap_id") or c.get("name", "")
            if cap_id in b_caps:
                gaps.append({"capability": cap_id, "label": b_caps[cap_id]["label"], "a_status": "missing", "b_level": b_caps[cap_id]["level"], "significance": "high"})
        return gaps

    def _calc_future_alignment(self, node_a_id, ctx_a):
        try:
            from app.universe.possibility_engine import get_possibility_engine
            engine = get_possibility_engine()
            graph = engine.build_graph(node_a_id, ctx_a.node_type if ctx_a else "company")
            return 0.7 if (graph and graph.transitions) else 0.5
        except Exception:
            return 0.5

    def _calc_reputation_match(self, node_a_id, node_b_id):
        try:
            from app.universe.reputation_engine import get_reputation_engine
            re = get_reputation_engine()
            pa = re.get_profile(node_a_id)
            pb = re.get_profile(node_b_id)
            sa = pa.overall_score / 100.0 if pa else 0
            sb = pb.overall_score / 100.0 if pb else 0
            if sa == 0 and sb == 0: return 0.5
            avg = (sa + sb) / 2.0
            gap = abs(sa - sb)
            return round(avg * (1.0 - gap * 0.3), 2)
        except Exception:
            return 0.5

    def _check_existing_relationship(self, node_a_id, node_b_id):
        try:
            from app.universe.relationship_engine import get_relationship_engine
            engine = get_relationship_engine()
            rel = engine.get_relationship(node_a_id, node_b_id)
            if not rel:
                return {"exists": False, "stage": "NONE"}
            return {"exists": True, "stage": rel.stage, "trust": rel.relationship_trust.get("overall", 0), "level": rel.relationship_trust.get("level", "N/A"), "total_projects": rel.total_projects, "successful_projects": rel.successful_projects, "duration_days": rel.duration_days}
        except Exception:
            return {"exists": False, "stage": "UNKNOWN"}

    def _calc_expected_value(self, reasons):
        gaps = reasons.get("capability_gap", [])
        cap_gain = min(len(gaps) * 0.2, 1.0) if gaps else 0.1
        fa = reasons.get("future_alignment", 0.5)
        rm = reasons.get("reputation_match", 0.5)
        growth = fa * 0.7 + cap_gain * 0.3
        strategic = fa * 0.5 + rm * 0.5
        overall = cap_gain * 0.35 + growth * 0.30 + strategic * 0.20 + rm * 0.15
        return {"capability_gain": round(cap_gain, 2), "growth_acceleration": round(growth, 2), "strategic_value": round(strategic, 2), "overall": round(overall, 2)}

    def _detect_risks(self, opp, ctx_b):
        risks = []
        try:
            from app.universe.reputation_engine import get_reputation_engine
            re = get_reputation_engine()
            pb = re.get_profile(opp.node_b_id)
            if not pb or pb.status == "UNKNOWN":
                risks.append(RiskSignal(category="reputation", severity="high", description="insufficient_reputation_data", mitigation="Wait for more reputation data before committing to a large engagement."))
            elif pb.dimensions.get("delivery") and pb.dimensions["delivery"].score < 40:
                risks.append(RiskSignal(category="reputation", severity="medium", description="low_delivery_trust", mitigation="Start with a small pilot project to verify delivery capability."))
        except Exception:
            pass
        er = opp.existing_relationship
        if er.get("stage") == "ENDED":
            risks.append(RiskSignal(category="relationship", severity="high", description="previous_relationship_ended", mitigation="Review why the previous relationship ended before re-engaging."))
        if er.get("exists") and er.get("total_projects", 0) > 0:
            total = er["total_projects"]
            success = er.get("successful_projects", 0)
            if (total - success) / total > 0.3:
                risks.append(RiskSignal(category="relationship", severity="medium", description="high_historical_failure_rate", mitigation="Investigate root causes of past failures before proceeding."))
        return risks[:6]

    def _generate_next_steps(self, opp):
        steps = []
        er = opp.existing_relationship
        if not er.get("exists") or er.get("stage") == "NONE":
            steps.append(NextStep(action="Send introduction request", rationale="No prior relationship exists.", timeframe="immediate", expected_outcome="Open communication channel"))
            steps.append(NextStep(action="Review capability complementarity", rationale="Validate capability fit before committing.", timeframe="short_term", expected_outcome="Confirmed fit"))
        elif er.get("stage") in ("DISCOVERED", "CONNECTED", "ACTIVE"):
            steps.append(NextStep(action="Progress relationship through lifecycle", rationale=f"Currently at {er.get('stage', 'unknown')} stage.", timeframe="short_term", expected_outcome="Relationship growth"))
        elif er.get("stage") == "ENDED":
            steps.append(NextStep(action="Review termination reason first", rationale="Previous relationship ended.", timeframe="immediate", expected_outcome="Understand root cause"))
        if not er.get("exists"):
            try:
                from app.universe.reputation_engine import get_reputation_engine
                re = get_reputation_engine()
                pb = re.get_profile(opp.node_b_id)
                if pb and pb.status == "UNKNOWN":
                    steps.append(NextStep(action="Request evidence from candidate", rationale="Build reputation baseline.", timeframe="short_term", expected_outcome="Reputation established"))
            except Exception:
                pass
        return steps

    def _calc_opportunity_score(self, opp):
        gaps = opp.reasons.get("capability_gap", [])
        cap_comp = min(len(gaps) * 0.2, 1.0) if gaps else 0.15
        fa = opp.reasons.get("future_alignment", 0.5)
        rm = opp.reasons.get("reputation_match", 0.5)
        er = opp.existing_relationship
        if er.get("exists"):
            trust = er.get("trust", 0) / 100.0
            sr = er["successful_projects"] / max(er["total_projects"], 1) if er.get("total_projects", 0) > 0 else 0.5
            rh = trust * 0.6 + sr * 0.4
        else:
            rh = 0.5
        strategic = opp.expected_value.get("strategic_value", 0.5)
        score = cap_comp * 0.30 + fa * 0.20 + rm * 0.20 + rh * 0.15 + strategic * 0.15
        penalty = 0
        for r in opp.risks:
            if r.severity in ("critical",): penalty += 0.15
            elif r.severity == "high": penalty += 0.10
            elif r.severity == "medium": penalty += 0.05
        return round(max(0.0, score - penalty), 2)

    def _calc_connection_value(self, opp):
        ev = opp.expected_value
        from app.universe.opportunity_memory import ConnectionValueVector
        return ConnectionValueVector.from_expected_value(ev)

    def _record_opportunity_created(self, opp):
        try:
            from app.universe.opportunity_memory import get_opportunity_memory_engine
            mem = get_opportunity_memory_engine()
            ev = mem.record_created(
                opportunity_id=opp.opportunity_id,
                node_a_id=opp.node_a_id,
                node_b_id=opp.node_b_id,
                confidence=opp.confidence,
                reason=opp.recommended_action,
                details={"reputation_match": opp.reasons.get("reputation_match", 0),
                         "future_alignment": opp.reasons.get("future_alignment", 0),
                         "expected_value": opp.expected_value.get("overall", 0)},
            )
            return ev.event_id
        except Exception:
            return ""

    def _generate_recommendation(self, opp):
        score = opp.confidence
        er = opp.existing_relationship
        if er.get("stage") == "ENDED":
            return "Not recommended: prior relationship ended." if score < 0.6 else "Consider re-engagement with caution."
        if score >= 0.80:
            return "Strongly recommended: establish strategic partnership."
        elif score >= 0.60:
            return "Recommended: establish cooperation."
        elif score >= 0.35:
            return "Consider with caution: moderate alignment."
        else:
            return "Not recommended at this time: insufficient alignment."

# ========== Relationship Intelligence Engine ==========

class RelationshipIntelligenceEngine:
    _instance = None

    def __init__(self):
        self.evaluator = OpportunityEvaluator()
        self._opportunities: Dict[str, RelationshipOpportunity] = {}
        self._node_opps: Dict[str, List[str]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    def evaluate_pair(self, node_a_id, node_b_id, node_a_name="", node_b_name="", node_a_type="company", node_b_type="company"):
        opp = self.evaluator.evaluate(node_a_id, node_b_id, node_a_name, node_b_name, node_a_type, node_b_type)
        self._opportunities[opp.opportunity_id] = opp
        for nid in (node_a_id, node_b_id):
            self._node_opps.setdefault(nid, [])
            if opp.opportunity_id not in self._node_opps[nid]:
                self._node_opps[nid].append(opp.opportunity_id)
        try:
            from app.universe.opportunity_memory import get_opportunity_memory_engine
            mem = get_opportunity_memory_engine()
            adjusted = mem.get_adjusted_confidence(opp.opportunity_id, opp.confidence)
            if adjusted != opp.confidence:
                opp.original_confidence = opp.confidence
                opp.confidence = adjusted
        except Exception:
            pass
        return opp

    def evaluate_candidates(self, node_id, candidate_ids, node_name="", node_type="company"):
        results = []
        for cid in candidate_ids:
            try:
                opp = self.evaluate_pair(node_id, cid, node_name or node_id, cid, node_type)
                results.append(opp)
            except Exception:
                pass
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    def get_opportunities(self, node_id):
        opp_ids = self._node_opps.get(node_id, [])
        result = []
        for oid in opp_ids:
            opp = self._opportunities.get(oid)
            if opp: result.append(opp.to_dict())
        result.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return result

    def get_opportunity(self, opportunity_id):
        opp = self._opportunities.get(opportunity_id)
        return opp.to_dict() if opp else None

    def from_connection_report(self, node_id, node_name="", node_type="company"):
        try:
            from app.universe.connection_engine import get_connection_engine
            c4 = get_connection_engine()
            report = c4.discover_connections(node_id, node_type)
        except Exception as e:
            return {"error": str(e), "opportunities": []}
        if not report or not report.candidates:
            return {"node_id": node_id, "candidates_found": 0, "opportunities": []}
        cids = [c.candidate_node_id for c in report.candidates]
        opps = self.evaluate_candidates(node_id, cids, node_name, node_type)
        c4m = {c.candidate_node_id: c for c in report.candidates}
        results = []
        for opp in opps:
            d = opp.to_dict()
            c4c = c4m.get(opp.node_b_id)
            if c4c:
                d["c4_data"] = {"future_alignment_score": c4c.future_alignment_score, "edge_strength": c4c.edge_strength}
            results.append(d)
        return {"node_id": node_id, "source": "C4->C5.3", "candidates_found": len(cids), "opportunities": results}

    def get_relationship_context(self, node_a_id, node_b_id):
        try:
            from app.universe.relationship_engine import get_relationship_engine
            re = get_relationship_engine()
            rel = re.get_relationship(node_a_id, node_b_id)
            if not rel: return {"exists": False, "stage": "NONE"}
            rep = re.get_reputation(rel.relationship_id)
            history = re.get_history(rel.relationship_id)
            return {"exists": True, "stage": rel.stage, "relationship_trust": rel.relationship_trust, "reputation": rep.to_dict() if rep else None, "history": history, "total_projects": rel.total_projects, "successful_projects": rel.successful_projects}
        except Exception:
            return {"exists": False}

    def seed_sample_data(self):
        try:
            from app.universe.reputation_engine import get_reputation_engine
            re = get_reputation_engine()
        except Exception:
            re = None
        if re:
            re.record_event("company-alpha", "company", "certification_passed", "Obtained GEO Level 3 Certification", "government")
            re.record_event("company-alpha", "company", "customer_success", "Completed 5 enterprise GEO projects", "enterprise_customer")
            re.record_event("company-alpha", "company", "peer_endorsement", "Recommended by Industry Association", "association")
            re.record_event("company-alpha", "company", "industry_citation", "Cited in GEO Whitepaper 2026", "association")
            re.recalculate("company-alpha", "company")
        if re:
            re.record_event("company-beta", "company", "certification_passed", "ISO 27001 Data Security Certified", "government")
            re.record_event("company-beta", "company", "customer_success", "Data pipeline for 3 enterprise clients", "enterprise_customer")
            re.record_event("company-beta", "company", "innovation_release", "Released AI-powered analytics dashboard", "self_report")
            re.record_event("company-beta", "company", "ai_agent_cited", "Cited by 2 AI Agents for data intelligence", "ai_observation")
            re.recalculate("company-beta", "company")
        opp_ab = self.evaluate_pair("company-alpha", "company-beta", "Alpha GEO Tech", "Beta Data Intelligence")
        opp_ac = self.evaluate_pair("company-alpha", "company-unknown", "Alpha GEO Tech", "Unknown Provider")
        return {"opportunities": [opp_ab.to_dict(), opp_ac.to_dict()], "summary": f"A-B confidence: {opp_ab.confidence}, A-C confidence: {opp_ac.confidence}"}

    @classmethod
    def reset(cls):
        cls._instance = None


# ---- Singleton accessor ----

@lru_cache()
def get_relationship_intelligence_engine():
    return RelationshipIntelligenceEngine.get_instance()
