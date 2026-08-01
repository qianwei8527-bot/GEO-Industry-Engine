"""C6.10 UniverseHomeService - assembles a node's own Universe view.

The service loads base data from DB, then projects it through:
  Context Engine    -> identity / position / memory / capability
  Reputation Engine -> trust state
  Ecosystem Graph   -> structure / relation / causality / evolution
  Possibility       -> future paths
  Connection        -> next connections / opportunities

The frontend never has to prepare extra_data.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy import select, func, or_

from app.models.company import Company
from app.models.provider import Provider
from app.models.industry import Industry
from app.models.relationship import Relationship
from app.models.capability import Capability
from app.models.provider_capability import ProviderCapability
from app.models.evidence import Evidence

from app.universe.context_engine import get_context_engine
from app.universe.reputation_engine import get_reputation_engine
from app.universe.memory_engine import get_memory_engine
from app.universe.ecosystem_graph import get_ecosystem_graph_engine
from app.universe.possibility_engine import get_possibility_engine


class UniverseHomeService:
    """Aggregate a node's identity, position, story, ecosystem, future, opportunities."""

    async def build(self, db, node_type: str, node_id: str) -> Dict[str, Any]:
        extra = await self._load_base(db, node_type, node_id)

        ctx = get_context_engine().understand(node_id, node_type, extra)
        graph = get_ecosystem_graph_engine().explain(node_id, node_type, extra)
        rep_snap = await self._reputation(db, node_id)
        possibility = self._possibility(node_id, node_type, extra)
        velocity = self._velocity(node_id)

        story = {
            "timeline": ctx.historical_memory,
            "velocity": velocity,
            "causality": graph.get("causality", {}),
            "evolution": graph.get("evolution", {}),
            "milestones": graph.get("evolution", {}).get("milestones", []),
        }

        future = {
            "possibility": possibility,
            "connection_needs": graph.get("next_connections", {}).get("needs", []),
            "candidates": graph.get("next_connections", {}).get("candidates", []),
            "direction": ctx.recommended_direction,
        }

        opportunities = {
            "connection_candidates": graph.get("next_connections", {}).get("candidates", []),
            "count": graph.get("next_connections", {}).get("candidate_count", 0),
        }

        return {
            "node_id": node_id,
            "node_type": node_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "identity": ctx.identity,
            "position": {
                "current": ctx.current_position,
                "industry": ctx.industry_context,
                "reputation": rep_snap.get("overview", {}) if rep_snap else {},
                "capabilities": ctx.capability_state,
                "risks": ctx.risk_assessment,
            },
            "story": story,
            "ecosystem": graph,
            "future": future,
            "opportunities": opportunities,
        }

    # ---- DB loading (service-side, not frontend-side) ----

    async def _load_base(self, db, node_type: str, node_id: str) -> Dict[str, Any]:
        uid = self._to_uuid(node_id)
        extra: Dict[str, Any] = {"name": node_id}

        if node_type == "company":
            company = await db.get(Company, uid) if isinstance(uid, uuid.UUID) else None
            if company:
                extra = {
                    "name": company.name,
                    "description": getattr(company, "description", "") or "",
                    "industry_id": str(company.industry_id) if company.industry_id else "",
                    "region": getattr(company, "region", "") or "",
                    "geo_score": company.geo_score or 0,
                    "trust_score": getattr(company, "trust_score", 0) or 0,
                    "evidence_count": await self._count(db, Evidence, Evidence.entity_id, uid),
                    "capability_count": await self._count(db, Capability, Capability.company_id, uid),
                    "relationship_count": await self._relationship_count(db, uid),
                    "relationships_list": await self._relationships(db, uid),
                }
                if extra["industry_id"]:
                    industry = await db.get(Industry, uuid.UUID(extra["industry_id"]))
                    extra["industry_name"] = industry.name if industry else ""
        elif node_type == "provider":
            provider = await db.get(Provider, uid) if isinstance(uid, uuid.UUID) else None
            if provider:
                extra = {
                    "name": f"Provider {str(uid)[:8]}",
                    "trust_score": provider.trust_score or 0,
                    "geo_score": provider.geo_score or 0,
                    "evidence_count": await self._count(db, Evidence, Evidence.entity_id, uid),
                    "capability_count": await self._count(db, ProviderCapability, ProviderCapability.provider_id, uid),
                    "relationship_count": await self._relationship_count(db, uid),
                    "relationships_list": await self._relationships(db, uid),
                }
        return extra

    async def _reputation(self, db, node_id: str) -> Optional[Dict[str, Any]]:
        try:
            re = get_reputation_engine()
            if not re.event_store.get_events(node_id):
                await re.restore_from_db(db, node_id)
            profile = re.get_profile(node_id)
            return profile.to_dict() if profile else None
        except Exception:
            return None

    def _possibility(self, node_id: str, node_type: str, extra: Dict) -> Dict[str, Any]:
        try:
            graph = get_possibility_engine().project_from_data(node_id, node_type, extra)
            return graph.to_dict()
        except Exception as e:
            return {"error": str(e), "states": {}, "transitions": []}

    def _velocity(self, node_id: str) -> Dict[str, Any]:
        try:
            return get_memory_engine().get_growth_velocity(node_id)
        except Exception:
            return {"trend": "unknown"}

    async def _count(self, db, model, column, uid) -> int:
        if not isinstance(uid, uuid.UUID):
            return 0
        return (await db.execute(select(func.count(model.id)).where(column == uid))).scalar() or 0

    async def _relationship_count(self, db, uid) -> int:
        if not isinstance(uid, uuid.UUID):
            return 0
        return (await db.execute(select(func.count(Relationship.id)).where(
            or_(Relationship.source_id == uid, Relationship.target_id == uid)
        ))).scalar() or 0

    async def _relationships(self, db, uid):
        if not isinstance(uid, uuid.UUID):
            return []
        rows = (await db.execute(select(Relationship).where(
            or_(Relationship.source_id == uid, Relationship.target_id == uid)
        ))).scalars().all()
        out = []
        for r in rows:
            other = r.target_id if r.source_id == uid else r.source_id
            if not other:
                continue
            out.append({
                "node_id": str(other),
                "type": r.relation_type,
                "stage": "CONNECTED",
                "strength": r.weight or 0,
                "direction": "bidirectional",
                "description": r.description or "",
            })
        return out

    @staticmethod
    def _to_uuid(node_id: str):
        try:
            return uuid.UUID(node_id) if len(node_id) == 36 else node_id
        except ValueError:
            return node_id


def get_universe_home_service() -> UniverseHomeService:
    return UniverseHomeService()
