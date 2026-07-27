from dataclasses import dataclass
from typing import List, Optional
from app.domain.evidence.evidence import Evidence, ConfidenceLevel

@dataclass
class TrustScore:
    entity_id: str
    score: float
    evidence_count: int
    max_confidence: ConfidenceLevel
    breakdown: dict

class TrustService:
    @staticmethod
    def compute(entity_id: str, evidence_list: List[Evidence]) -> TrustScore:
        if not evidence_list:
            return TrustScore(
                entity_id=entity_id, score=0.0, evidence_count=0,
                max_confidence=ConfidenceLevel.L0_SELF_REPORTED, breakdown={}
            )
        weights = {
            ConfidenceLevel.L0_SELF_REPORTED: 0.2,
            ConfidenceLevel.L1_PLATFORM_VERIFIED: 0.4,
            ConfidenceLevel.L2_THIRD_PARTY: 0.6,
            ConfidenceLevel.L3_MARKET_VALIDATED: 0.8,
            ConfidenceLevel.L4_AI_CROSS_VERIFIED: 1.0,
        }
        total = sum(weights[e.confidence_level] for e in evidence_list)
        score = min(100.0, total / len(evidence_list) * 100)
        max_conf = max(e.confidence_level for e in evidence_list)
        return TrustScore(
            entity_id=entity_id, score=round(score, 1),
            evidence_count=len(evidence_list), max_confidence=max_conf,
            breakdown={"by_level": {lv.value: sum(1 for e in evidence_list if e.confidence_level == lv) for lv in ConfidenceLevel}}
        )
