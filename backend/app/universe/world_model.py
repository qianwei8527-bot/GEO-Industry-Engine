# GEO Universe Living World Model
# The World Model manages emerging knowledge - concepts the Universe
# has observed but not yet fully integrated.
#
# Pipeline:
#   Observation -> Evidence -> KnowledgeCandidate -> WorldModelProposal
#   -> Law Governance -> Universe Adoption
#
# Constraints:
#   - never mutates Registry automatically
#   - never bypasses Law Governance
#   - synthetic signals never become real world structure

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from functools import lru_cache
import uuid

from app.universe.registry import UniverseRegistry, get_registry
from app.universe.event_backbone import UniverseEvent, get_event_backbone


@dataclass
class KnowledgeCandidate:
    """A concept the Universe is observing but has not yet confirmed."""
    candidate_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""  # node_type | capability | relationship | role
    confidence: float = 0.0
    evidence_count: int = 0
    first_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sources: List[str] = field(default_factory=list)
    affected_domains: List[str] = field(default_factory=list)
    signals: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "observed"  # observed | emerging | recognized | proposed | adopted | rejected
    evidence_ids: List[str] = field(default_factory=list)
    observation_ids: List[str] = field(default_factory=list)
    provenance: List[Dict[str, Any]] = field(default_factory=list)
    is_synthetic: bool = False
    proposal_id: Optional[str] = None
    adoption_record: Optional[Dict[str, Any]] = None
    recognized_by: Optional[str] = None

    def promote(self):
        """Move to next status level."""
        transitions = {"observed": "emerging", "emerging": "recognized", "recognized": "proposed"}
        self.status = transitions.get(self.status, self.status)

    def add_signal(self, signal: Dict[str, Any], evidence_id: str = None, observation_id: str = None):
        self.signals.append(signal or {})
        self.evidence_count += 1
        self.last_seen = datetime.now(timezone.utc).isoformat()
        if evidence_id and evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)
        if observation_id and observation_id not in self.observation_ids:
            self.observation_ids.append(observation_id)
        if signal and signal.get("is_synthetic"):
            self.is_synthetic = True
        self.provenance.append({
            "evidence_id": evidence_id,
            "observation_id": observation_id,
            "source": (signal or {}).get("source", ""),
            "at": self.last_seen,
        })
        self._recalculate_confidence()

    def _recalculate_confidence(self):
        """Compute emergence score based on occurrence, source diversity, domain spread."""
        occ_score = min(self.evidence_count / 20.0, 1.0)
        source_diversity = min(len(set(self.sources)) / 6.0, 1.0)
        domain_spread = min(len(self.affected_domains) / 4.0, 1.0)
        self.confidence = round((occ_score * 0.4 + source_diversity * 0.35 + domain_spread * 0.25), 2)

    def can_be_recognized(self, evidence_status: str = "verified") -> bool:
        return (
            self.evidence_count >= 3
            and len(set(self.sources)) >= 2
            and evidence_status == "verified"
            and not self.is_synthetic
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "name": self.name,
            "category": self.category,
            "confidence": self.confidence,
            "evidence_count": self.evidence_count,
            "status": self.status,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "sources": self.sources,
            "affected_domains": self.affected_domains,
            "evidence_ids": self.evidence_ids,
            "observation_ids": self.observation_ids,
            "is_synthetic": self.is_synthetic,
            "proposal_id": self.proposal_id,
            "recognized_by": self.recognized_by,
        }


@dataclass
class WorldModelProposal:
    """A governed proposal to evolve the Universe ontology."""
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    candidate_key: str = ""
    concept_name: str = ""
    concept_type: str = ""
    status: str = "pending"  # pending | approved | rejected | adopted
    ontology_suggestion: Dict[str, Any] = field(default_factory=dict)
    evidence_ids: List[str] = field(default_factory=list)
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.0
    emergence_score: float = 0.0
    proposed_by: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""
    reason: str = ""
    law_ids: List[str] = field(default_factory=list)
    law_explanation: List[Dict[str, Any]] = field(default_factory=list)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    adopted_at: str = ""
    registry_update_pending: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "candidate_key": self.candidate_key,
            "concept_name": self.concept_name,
            "concept_type": self.concept_type,
            "status": self.status,
            "ontology_suggestion": self.ontology_suggestion,
            "evidence_ids": self.evidence_ids,
            "source_ids": self.source_ids,
            "confidence": self.confidence,
            "emergence_score": self.emergence_score,
            "proposed_by": self.proposed_by,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "reason": self.reason,
            "law_ids": self.law_ids,
            "law_explanation": self.law_explanation,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "adopted_at": self.adopted_at,
            "registry_update_pending": self.registry_update_pending,
        }


@dataclass
class IndustryContextModel:
    """Lightweight understanding of what is emerging in an industry."""
    industry_id: str = ""
    name: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    emerging_concepts: List[Dict[str, Any]] = field(default_factory=list)
    proposals: List[Dict[str, Any]] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "industry_id": self.industry_id,
            "name": self.name,
            "updated_at": self.updated_at,
            "emerging_concepts": self.emerging_concepts,
            "proposals": self.proposals,
            "evidence_ids": self.evidence_ids,
            "summary": self.summary,
        }


class LivingWorldModel:
    """Manages the Universe's emerging knowledge and governs the
    Observation -> Knowledge -> Proposal -> Law -> Adoption pipeline.

    This is NOT a static database. It represents what the Universe
    has learned so far and is currently learning.
    """

    _instance: Optional["LivingWorldModel"] = None

    def __init__(self):
        self.candidates: Dict[str, KnowledgeCandidate] = {}
        self.proposals: Dict[str, WorldModelProposal] = {}
        self.industry_contexts: Dict[str, IndustryContextModel] = {}
        self.integrated: List[Dict[str, Any]] = []
        self.learning_log: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "LivingWorldModel":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    # ---- Observe ----

    def observe(self, concept_name: str, category: str, source: str,
                domain: str = None, signal_data: Dict = None,
                evidence_id: str = None, observation_id: str = None,
                synthetic: bool = False) -> KnowledgeCandidate:
        """Record an observation of a potentially new concept.

        Existing candidates accumulate evidence. New concepts start as
        observed. Synthetic signals never leave the observation layer.
        """
        reg = get_registry()
        if reg.get_node_type(concept_name) or reg.get_capability(concept_name):
            self._log(f"Reinforced: {concept_name} (already integrated as {category})")
            return KnowledgeCandidate(name=concept_name, category=category,
                                      status="integrated", confidence=1.0)

        key = f"{category}:{concept_name.lower()}"
        signal = dict(signal_data or {})
        signal.setdefault("source", source)
        if synthetic:
            signal["is_synthetic"] = True

        if key in self.candidates:
            candidate = self.candidates[key]
            if source not in candidate.sources:
                candidate.sources.append(source)
            if domain and domain not in candidate.affected_domains:
                candidate.affected_domains.append(domain)
            candidate.add_signal(signal, evidence_id, observation_id)
        else:
            candidate = KnowledgeCandidate(
                name=concept_name,
                category=category,
                sources=[source],
                affected_domains=[domain] if domain else [],
                is_synthetic=synthetic,
            )
            candidate.add_signal(signal, evidence_id, observation_id)
            self.candidates[key] = candidate

        if candidate.status == "observed" and candidate.confidence >= 0.3:
            candidate.promote()
            self._log(f"Promoted to emerging: {concept_name}")
        return candidate

    # ---- Recognize ----

    def recognize(self, candidate_key: str, evidence_status: str = "verified",
                  reviewer: str = None) -> KnowledgeCandidate:
        """Recognize a candidate only when verified evidence is sufficient."""
        candidate = self.candidates.get(candidate_key)
        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_key}")
        if candidate.status not in ("observed", "emerging"):
            raise ValueError(f"Candidate {candidate_key} is already {candidate.status}")
        if not candidate.can_be_recognized(evidence_status):
            raise ValueError(
                "Cannot recognize: need 3+ evidence, 2+ sources, verified evidence, non-synthetic"
            )
        candidate.status = "recognized"
        candidate.recognized_by = reviewer
        self._log(f"Recognized: {candidate.name} ({candidate.category})")
        return candidate

    # ---- Propose ----

    def propose(self, candidate_key: str, proposed_by: str,
                ontology_suggestion: Dict = None, reason: str = "") -> WorldModelProposal:
        """Create a governed ontology proposal from a recognized candidate."""
        candidate = self.candidates.get(candidate_key)
        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_key}")
        if candidate.status != "recognized":
            raise ValueError("Only recognized candidates can be proposed")
        if candidate.is_synthetic:
            raise ValueError("Synthetic candidates cannot be proposed")
        if not proposed_by or proposed_by in ("system", "auto", "client"):
            raise ValueError("proposed_by must be a governance actor")

        proposal = WorldModelProposal(
            candidate_key=candidate_key,
            concept_name=candidate.name,
            concept_type=candidate.category,
            ontology_suggestion=ontology_suggestion or {},
            evidence_ids=list(candidate.evidence_ids),
            source_ids=list(candidate.sources),
            confidence=candidate.confidence,
            emergence_score=candidate.confidence,
            proposed_by=proposed_by,
            reason=reason,
        )
        self.proposals[proposal.proposal_id] = proposal
        candidate.proposal_id = proposal.proposal_id
        candidate.status = "proposed"
        get_event_backbone().emit(UniverseEvent(
            node_id=f"world:{candidate.name}",
            domain="world_model",
            event_type="ontology.proposal_created",
            actor_id=proposed_by,
            source="world_model",
            payload={
                "proposal_id": proposal.proposal_id,
                "concept_name": candidate.name,
                "concept_type": candidate.category,
                "correlation_id": proposal.correlation_id,
            },
        ))
        self._log(f"Proposed: {candidate.name} -> {candidate.category} ontology")
        return proposal

    # ---- Governance ----

    async def review_proposal(self, proposal_id: str, actor: str, decision: str,
                              reason: str = "", evidence_status: str = "verified") -> WorldModelProposal:
        """Review a proposal. Approval requires Law Governance; rejection requires reason."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        if proposal.status != "pending":
            raise ValueError(f"Proposal is already {proposal.status}")
        if not actor or actor in ("system", "auto", "client"):
            raise ValueError("review must come from a human governance actor")
        if decision not in ("approved", "rejected"):
            raise ValueError("decision must be approved or rejected")

        candidate = self.candidates.get(proposal.candidate_key)
        if not candidate:
            raise ValueError(f"Candidate not found: {proposal.candidate_key}")

        if decision == "rejected":
            if not reason:
                raise ValueError("rejection requires a reason")
            proposal.status = "rejected"
            proposal.reviewed_by = actor
            proposal.reviewed_at = datetime.now(timezone.utc).isoformat()
            proposal.reason = reason
            candidate.status = "recognized"
            self._log(f"Proposal rejected: {candidate.name} ({reason})")
            return proposal

        from app.universe.law_engine import get_law_engine
        event = UniverseEvent(
            node_id=f"world:{candidate.name}",
            domain="world_model",
            event_type="ontology.proposal_approved",
            actor_id=actor,
            source="governance",
            payload={
                "proposal_id": proposal.proposal_id,
                "concept_name": candidate.name,
                "concept_type": candidate.category,
                "evidence_status": evidence_status,
            },
        )
        law_result = await get_law_engine().handle(
            event,
            context={"evidence_status": evidence_status, "source_type": "governance"},
        )
        if "ontology_adoption_governance" not in law_result.get("applied_laws", []):
            raise ValueError("Law governance did not approve ontology adoption")

        proposal.status = "approved"
        proposal.reviewed_by = actor
        proposal.reviewed_at = datetime.now(timezone.utc).isoformat()
        proposal.reason = reason
        proposal.law_ids = law_result.get("applied_laws", [])
        proposal.law_explanation = law_result.get("explanation", [])
        self._log(f"Proposal approved: {candidate.name} via {proposal.law_ids}")
        return proposal

    def adopt(self, proposal_id: str, actor: str) -> WorldModelProposal:
        """Adopt an approved proposal. Never mutates Registry automatically."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        if proposal.status != "approved":
            raise ValueError("Only approved proposals can be adopted")
        if not actor or actor in ("system", "auto", "client"):
            raise ValueError("adoption must come from a governance actor")

        candidate = self.candidates.get(proposal.candidate_key)
        if not candidate:
            raise ValueError(f"Candidate not found: {proposal.candidate_key}")

        proposal.status = "adopted"
        proposal.adopted_at = datetime.now(timezone.utc).isoformat()
        proposal.registry_update_pending = True
        candidate.status = "adopted"
        candidate.adoption_record = {
            "proposal_id": proposal.proposal_id,
            "adopted_at": proposal.adopted_at,
            "registry_update_pending": True,
        }
        self.integrated.append({
            "name": candidate.name,
            "category": candidate.category,
            "adopted_at": proposal.adopted_at,
            "evidence_count": candidate.evidence_count,
            "confidence": candidate.confidence,
            "sources": candidate.sources,
            "registry_update_pending": True,
        })
        get_event_backbone().emit(UniverseEvent(
            node_id=f"world:{candidate.name}",
            domain="world_model",
            event_type="ontology.concept_adopted",
            actor_id=actor,
            source="governance",
            payload={
                "proposal_id": proposal.proposal_id,
                "registry_update_pending": True,
                "correlation_id": proposal.correlation_id,
            },
        ))
        self._log(f"Adopted: {candidate.name} (registry update pending)")
        return proposal

    # ---- Industry Context ----

    def assess_industry(self, industry_id: str, name: str = None,
                        evidence_ids: List[str] = None, summary: str = None) -> IndustryContextModel:
        """Build a lightweight context view for an industry from current candidates."""
        matched_keys = [
            key for key, c in self.candidates.items()
            if industry_id in c.affected_domains
        ]
        emerging = [
            c.to_dict() for key, c in self.candidates.items()
            if key in matched_keys and c.status in ("observed", "emerging", "recognized", "proposed")
        ]
        proposals = [
            p.to_dict() for p in self.proposals.values()
            if p.candidate_key in matched_keys
        ]
        evidence = list(evidence_ids or [])
        if not evidence:
            for key, c in self.candidates.items():
                if key in matched_keys:
                    for eid in c.evidence_ids:
                        if eid not in evidence:
                            evidence.append(eid)
        ctx = IndustryContextModel(
            industry_id=industry_id,
            name=name or industry_id,
            emerging_concepts=emerging,
            proposals=proposals,
            evidence_ids=evidence,
            summary=summary or f"{len(matched_keys)} concepts observed in {industry_id}",
        )
        self.industry_contexts[industry_id] = ctx
        return ctx

    # ---- Query ----

    def get_emerging(self, min_confidence: float = 0.0) -> List[KnowledgeCandidate]:
        return [c for c in self.candidates.values()
                if c.status in ("observed", "emerging") and c.confidence >= min_confidence]

    def get_recognized(self) -> List[KnowledgeCandidate]:
        return [c for c in self.candidates.values() if c.status == "recognized"]

    def get_candidate(self, key: str) -> Optional[KnowledgeCandidate]:
        return self.candidates.get(key)

    def list_all(self) -> List[KnowledgeCandidate]:
        return list(self.candidates.values())

    def get_proposal(self, proposal_id: str) -> Optional[WorldModelProposal]:
        return self.proposals.get(proposal_id)

    def list_proposals(self, status: str = None) -> List[WorldModelProposal]:
        proposals = list(self.proposals.values())
        if status:
            proposals = [p for p in proposals if p.status == status]
        return proposals

    def get_industry_context(self, industry_id: str) -> Optional[IndustryContextModel]:
        return self.industry_contexts.get(industry_id)

    # ---- Stats ----

    def stats(self) -> Dict[str, Any]:
        by_status = {}
        for c in self.candidates.values():
            by_status.setdefault(c.status, 0)
            by_status[c.status] += 1
        proposals_by_status = {}
        for p in self.proposals.values():
            proposals_by_status.setdefault(p.status, 0)
            proposals_by_status[p.status] += 1
        return {
            "total_candidates": len(self.candidates),
            "by_status": by_status,
            "proposals": proposals_by_status,
            "integrated_count": len(self.integrated),
            "industry_contexts": len(self.industry_contexts),
            "recent_learning": self.learning_log[-5:],
        }

    def export_full(self) -> Dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates.values()],
            "proposals": [p.to_dict() for p in self.proposals.values()],
            "industry_contexts": [c.to_dict() for c in self.industry_contexts.values()],
            "integrated": self.integrated,
            "stats": self.stats(),
            "learning_log": self.learning_log[-20:],
        }

    def _log(self, message: str):
        self.learning_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
        })


def get_world_model() -> LivingWorldModel:
    return LivingWorldModel.get_instance()
