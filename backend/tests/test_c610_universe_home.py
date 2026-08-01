"""C6.10 Universe Home: service aggregation + Relationship value_creation fix."""

import sys
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

from sqlalchemy import select

from app.database import _get_session_factory
from app.models.company import Company
from app.services.universe_home import UniverseHomeService
from app.universe.relationship_engine import get_relationship_engine, RelationshipEngine


class TestUniverseHomeService:
    async def test_service_assembles_full_view(self):
        factory = _get_session_factory()
        async with factory() as db:
            company = (await db.execute(select(Company).limit(1))).scalars().first()
            if not company:
                return
            result = await UniverseHomeService().build(db, "company", str(company.id))
            assert result["node_id"] == str(company.id)
            assert result["node_type"] == "company"
            assert result["identity"]["name"] == company.name
            for key in ("identity", "position", "story", "ecosystem", "future", "opportunities"):
                assert key in result
            assert result["story"]["timeline"] is not None
            assert result["ecosystem"]["structure"] is not None
            assert "possibility" in result["future"]
            assert "connection_candidates" in result["opportunities"]

    async def test_service_falls_back_without_fabricated_identity(self):
        factory = _get_session_factory()
        async with factory() as db:
            result = await UniverseHomeService().build(db, "company", "unknown-node-id")
            assert result["identity"]["node_id"] == "unknown-node-id"
            assert result["story"]["causality"]["available"] is False


class TestRelationshipValueCreation:
    def setup_method(self):
        RelationshipEngine.reset()

    def test_relationship_reputation_does_not_crash(self):
        rel = get_relationship_engine()
        r = rel.create_relationship("a", "b", relationship_type="partnership")
        rel.transition(r.relationship_id, "DISCOVERED", event_type="discovered")
        rel.transition(r.relationship_id, "CONNECTED", event_type="connected")
        rel.transition(r.relationship_id, "ACTIVE", event_type="activated")
        rel.transition(r.relationship_id, "COLLABORATING", event_type="collaboration_started")
        rep = rel.get_reputation(r.relationship_id)
        assert rep is not None
        assert "value_creation" in rep.to_dict()["dimensions"]
        assert "value_creation" in r.relationship_trust
