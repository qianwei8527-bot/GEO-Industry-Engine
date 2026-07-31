"""P1-A: Provider search tool for agents."""
from typing import Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid


class ProviderSearchTool:
    """Finds and queries service providers in the GEO ecosystem."""

    def __init__(self):
        self._db = None

    def set_db(self, db: AsyncSession):
        self._db = db

    async def search(self, industry_id: Optional[str] = None, capability: Optional[str] = None,
                     min_trust: float = 0.0, limit: int = 10) -> List[dict]:
        """Search for providers by industry, capability keyword, or trust threshold."""
        from app.models.provider import Provider
        from app.models.provider_capability import ProviderCapability
        from app.models.capability import Capability

        query = select(Provider).where(Provider.is_active == True)
        if min_trust > 0:
            query = query.where(Provider.trust_score >= min_trust)

        result = await self._db.execute(query.limit(limit * 2))
        providers = result.scalars().all()

        output = []
        for p in providers:
            entry = {
                "id": str(p.id), "entity_id": str(p.entity_id),
                "provider_type": p.provider_type, "trust_score": p.trust_score,
                "geo_score": p.geo_score, "verification_status": p.verification_status,
                "avg_rating": p.avg_rating, "completed_orders": p.completed_orders,
            }
            # Fetch capabilities
            cap_result = await self._db.execute(
                select(ProviderCapability, Capability)
                .join(Capability, ProviderCapability.capability_id == Capability.id)
                .where(ProviderCapability.provider_id == p.id)
            )
            caps = []
            for pc, c in cap_result.all():
                caps.append({"name": c.name, "level": pc.level, "category": c.category, "verified": pc.verified})
            entry["capabilities"] = caps

            # Filter by capability keyword
            if capability and capability.lower() not in str(caps).lower():
                continue

            output.append(entry)
            if len(output) >= limit:
                break

        return output

    async def get_provider_details(self, provider_id: str) -> dict:
        """Get full provider profile with capabilities."""
        from app.models.provider import Provider
        from app.models.provider_capability import ProviderCapability
        from app.models.capability import Capability
        from app.models.entity import Entity

        uid = uuid.UUID(provider_id)
        result = await self._db.execute(select(Provider).where(Provider.id == uid))
        p = result.scalar_one_or_none()
        if not p:
            return {"error": f"Provider {provider_id} not found"}

        # Get entity info
        ent_result = await self._db.execute(select(Entity).where(Entity.id == p.entity_id))
        entity = ent_result.scalar_one_or_none()

        # Get capabilities
        cap_result = await self._db.execute(
            select(ProviderCapability, Capability)
            .join(Capability, ProviderCapability.capability_id == Capability.id)
            .where(ProviderCapability.provider_id == uid)
        )
        caps = [{"name": c.name, "level": pc.level, "category": c.category, "verified": pc.verified,
                 "experience_years": pc.experience_years} for pc, c in cap_result.all()]

        return {
            "id": str(p.id), "entity_id": str(p.entity_id),
            "entity_name": entity.name if entity else "Unknown",
            "provider_type": p.provider_type, "trust_score": p.trust_score,
            "geo_score": p.geo_score, "verification_status": p.verification_status,
            "pricing_model": p.pricing_model, "avg_rating": p.avg_rating,
            "completed_orders": p.completed_orders, "capabilities": caps,
        }


provider_search_tool = ProviderSearchTool()
