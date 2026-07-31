"""P1-A: Matching tool for agents - business opportunity matching."""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid


class MatchTool:
    """Wraps the Matching Engine for agent use. Finds business opportunities."""

    def __init__(self):
        self._db = None

    def set_db(self, db: AsyncSession):
        self._db = db

    async def find_matches(self, demand_id: str, limit: int = 5) -> dict:
        """Find matching providers for a market demand."""
        from app.matching.engine import MatchingEngine

        try:
            engine = MatchingEngine(self._db)
            results = await engine.match(demand_id)
            if isinstance(results, dict) and results.get("matches"):
                matches = results["matches"][:limit]
                return {
                    "demand_id": demand_id,
                    "matches": [{
                        "provider_id": m.get("provider_id", ""),
                        "score": m.get("score", 0),
                        "level": m.get("level", "standard"),
                        "reasons": m.get("reasons", []),
                    } for m in matches],
                    "total_matches": len(results["matches"]),
                }
            return {"demand_id": demand_id, "matches": [], "error": "No matching engine results"}
        except Exception as e:
            return {"error": str(e)}

    async def get_match_history(self, provider_id: str = "", demand_id: str = "", limit: int = 10) -> list:
        """Get historical match results."""
        from app.models.match_result import MatchResult

        query = select(MatchResult).order_by(MatchResult.score.desc())
        if provider_id:
            query = query.where(MatchResult.provider_id == uuid.UUID(provider_id))
        if demand_id:
            query = query.where(MatchResult.demand_id == uuid.UUID(demand_id))

        result = await self._db.execute(query.limit(limit))
        rows = result.scalars().all()

        return [{
            "id": str(r.id), "demand_id": str(r.demand_id), "provider_id": str(r.provider_id),
            "score": r.score, "rank": r.rank, "reasons": r.reasons, "status": r.status,
        } for r in rows]

    async def top_opportunities(self, industry_id: str = "", limit: int = 5) -> list:
        """Find top business opportunities by industry."""
        from app.models.market_demand import MarketDemand
        from app.models.match_result import MatchResult

        query = select(MarketDemand).where(MarketDemand.status == "open")
        if industry_id:
            query = query.where(MarketDemand.industry_id == uuid.UUID(industry_id))

        demands_result = await self._db.execute(query.limit(limit))
        demands = demands_result.scalars().all()

        opportunities = []
        for d in demands:
            match_result = await self._db.execute(
                select(MatchResult).where(MatchResult.demand_id == d.id).order_by(MatchResult.score.desc()).limit(3)
            )
            matches = match_result.scalars().all()
            opportunities.append({
                "demand_id": str(d.id), "title": d.title, "budget_range": str(d.budget_range) if d.budget_range else "",
                "top_matches": [{"provider_id": str(m.provider_id), "score": m.score} for m in matches],
            })
        return opportunities


match_tool = MatchTool()
