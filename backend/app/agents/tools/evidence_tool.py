"""P1-A: Evidence tool for agents - trust verification."""
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid


class EvidenceTool:
    """Queries and evaluates evidence for trust verification."""

    def __init__(self):
        self._db = None

    def set_db(self, db: AsyncSession):
        self._db = db

    async def get_evidence(self, entity_id: str, limit: int = 20) -> dict:
        """Get all evidence for an entity with trust summary."""
        from app.models.evidence import Evidence

        uid = uuid.UUID(entity_id)
        result = await self._db.execute(
            select(Evidence).where(Evidence.entity_id == uid).order_by(Evidence.confidence_level.desc()).limit(limit)
        )
        rows = result.scalars().all()

        if not rows:
            return {"entity_id": entity_id, "evidence": [], "summary": "No evidence found"}

        verified_count = sum(1 for e in rows if e.verified)
        avg_confidence = round(sum(e.confidence_level for e in rows) / len(rows), 2)

        return {
            "entity_id": entity_id,
            "total_evidence": len(rows),
            "verified_count": verified_count,
            "avg_confidence": avg_confidence,
            "trust_level": "A" if avg_confidence >= 0.8 else "B" if avg_confidence >= 0.6 else "C" if avg_confidence >= 0.4 else "D",
            "evidence": [{
                "id": str(e.id), "claim": e.claim[:200], "source_url": e.source_url,
                "confidence_level": e.confidence_level, "source_type": e.source_type,
                "verified": e.verified,
            } for e in rows[:10]],
        }

    async def verify_claim(self, entity_id: str, claim_keyword: str = "") -> dict:
        """Check if a specific claim has evidence support."""
        from app.models.evidence import Evidence

        query = select(Evidence).where(Evidence.entity_id == uuid.UUID(entity_id))
        if claim_keyword:
            query = query.where(Evidence.claim.ilike(f"%{claim_keyword}%"))

        result = await self._db.execute(query.limit(5))
        rows = result.scalars().all()

        return {
            "entity_id": entity_id,
            "claim_keyword": claim_keyword,
            "supported": len(rows) > 0,
            "matches": len(rows),
            "best_confidence": max((e.confidence_level for e in rows), default=0),
        }


evidence_tool = EvidenceTool()
