from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from app.models.evidence import Evidence


class EvidenceRetriever:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_evidence(self, target_id: str, min_confidence: int = 0) -> List[Evidence]:
        stmt = select(Evidence).where(
            Evidence.target_id == target_id,
            Evidence.confidence_level >= min_confidence,
        ).order_by(Evidence.confidence_level.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_evidence_count(self, target_id: str) -> int:
        stmt = select(Evidence).where(Evidence.target_id == target_id)
        result = await self.db.execute(stmt)
        return len(result.scalars().all())
