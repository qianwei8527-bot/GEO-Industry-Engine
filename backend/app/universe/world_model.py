# GEO Universe Living World Model
# The World Model manages emerging knowledge ? concepts the Universe
# has observed but not yet fully integrated.
#
# Pipeline: Observation -> Evidence -> KnowledgeCandidate -> WorldModel -> Registry

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from functools import lru_cache
import uuid

from app.universe.registry import UniverseRegistry, get_registry


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
    status: str = "observed"  # observed | emerging | recognized | integrated

    def promote(self):
        """Move to next status level."""
        transitions = {"observed": "emerging", "emerging": "recognized", "recognized": "integrated"}
        self.status = transitions.get(self.status, self.status)

    def add_signal(self, signal: Dict[str, Any]):
        self.signals.append(signal)
        self.evidence_count += 1
        self.last_seen = datetime.now(timezone.utc).isoformat()
        self._recalculate_confidence()

    def _recalculate_confidence(self):
        """Compute emergence score based on occurrence, persistence, source diversity."""
        occ_score = min(self.evidence_count / 50.0, 1.0)
        source_diversity = min(len(set(self.sources)) / 10.0, 1.0)
        domain_spread = min(len(self.affected_domains) / 5.0, 1.0)
        self.confidence = round((occ_score * 0.4 + source_diversity * 0.3 + domain_spread * 0.3), 2)


class LivingWorldModel:
    """Manages the Universe's emerging knowledge and governs the
    Observation -> Knowledge -> Registry pipeline.

    This is NOT a static database. It represents what the Universe
    has learned so far and is currently learning.
    """

    _instance: Optional["LivingWorldModel"] = None

    def __init__(self):
        self.candidates: Dict[str, KnowledgeCandidate] = {}
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
                domain: str = None, signal_data: Dict = None) -> KnowledgeCandidate:
        """Record an observation of a potentially new concept.

        If the concept already exists as a candidate, add evidence.
        If it's new, create a candidate.
        If it's already integrated, log as reinforcement.
        """
        # Check if already integrated
        reg = get_registry()
        if reg.get_node_type(concept_name):
            self._log(f"Reinforced: {concept_name} (already integrated as {category})")
            return KnowledgeCandidate(name=concept_name, category=category, status="integrated", confidence=1.0)

        # Find or create candidate
        key = f"{category}:{concept_name.lower()}"
        if key in self.candidates:
            candidate = self.candidates[key]
            if signal_data:
                candidate.add_signal(signal_data)
            if source not in candidate.sources:
                candidate.sources.append(source)
            if domain and domain not in candidate.affected_domains:
                candidate.affected_domains.append(domain)

            # Auto-promote based on confidence
            if candidate.confidence >= 0.3 and candidate.status == "observed":
                candidate.promote()
                self._log(f"Promoted to emerging: {concept_name}")
            elif candidate.confidence >= 0.6 and candidate.status == "emerging":
                candidate.promote()
                self._log(f"Promoted to recognized: {concept_name}")
        else:
            candidate = KnowledgeCandidate(
                name=concept_name,
                category=category,
                evidence_count=1,
                sources=[source],
                affected_domains=[domain] if domain else [],
                status="observed",
            )
            candidate._recalculate_confidence()
            self.candidates[key] = candidate
            self._log(f"New observation: {concept_name} (category: {category})")

        return candidate

    # ---- Recognize ----

    def recognize(self, candidate_key: str) -> Optional[Dict[str, Any]]:
        """Manually recognize a knowledge candidate and integrate it
        into the Living World Model. Returns the integration record."""
        candidate = self.candidates.get(candidate_key)
        if not candidate:
            return None

        candidate.status = "integrated"
        record = {
            "name": candidate.name,
            "category": candidate.category,
            "integrated_at": datetime.now(timezone.utc).isoformat(),
            "evidence_count": candidate.evidence_count,
            "confidence": candidate.confidence,
            "sources": candidate.sources,
        }
        self.integrated.append(record)
        self._log(f"Integrated: {candidate.name} into {candidate.category}")
        return record

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

    # ---- Stats ----

    def stats(self) -> Dict[str, Any]:
        by_status = {}
        for c in self.candidates.values():
            by_status.setdefault(c.status, 0)
            by_status[c.status] += 1
        return {
            "total_candidates": len(self.candidates),
            "integrated_count": len(self.integrated),
            "by_status": by_status,
            "recent_learning": self.learning_log[-5:],
        }

    def export_full(self) -> Dict[str, Any]:
        return {
            "candidates": [
                {
                    "key": key,
                    "name": c.name,
                    "category": c.category,
                    "confidence": c.confidence,
                    "evidence_count": c.evidence_count,
                    "status": c.status,
                    "first_seen": c.first_seen,
                    "sources": c.sources,
                    "affected_domains": c.affected_domains,
                }
                for key, c in self.candidates.items()
            ],
            "integrated": self.integrated,
            "stats": self.stats(),
            "learning_log": self.learning_log[-20:],
        }

    def _log(self, message: str):
        self.learning_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
        })


@lru_cache()
def get_world_model() -> LivingWorldModel:
    return LivingWorldModel.get_instance()
