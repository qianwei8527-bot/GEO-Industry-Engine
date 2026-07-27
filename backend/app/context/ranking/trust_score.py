from sqlalchemy.ext.asyncio import AsyncSession
from app.context.retrieval.evidence_retriever import EvidenceRetriever

CONFIDENCE_WEIGHTS = {0: 0.2, 1: 0.4, 2: 0.6, 3: 0.8, 4: 1.0}


class TrustScorer:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compute(self, entity_id: str) -> dict:
        retriever = EvidenceRetriever(self.db)
        evidence_list = await retriever.get_evidence(entity_id)
        if not evidence_list:
            return {"score": 0.0, "count": 0, "max_confidence": 0, "by_level": {}}
        weights = [CONFIDENCE_WEIGHTS.get(e.confidence_level, 0.2) for e in evidence_list]
        score = min(100.0, sum(weights) / len(weights) * 100)
        max_conf = max(e.confidence_level for e in evidence_list)
        by_level = {}
        for ev in evidence_list:
            by_level[ev.confidence_level] = by_level.get(ev.confidence_level, 0) + 1
        return {"score": round(score, 1), "count": len(evidence_list), "max_confidence": max_conf, "by_level": by_level}
