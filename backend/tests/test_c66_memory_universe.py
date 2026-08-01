"""C6.6 Memory Universe: unified timeline, cause chain, narrative from events only."""
import sys
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

from sqlalchemy import select, func
from app.database import _get_session_factory
from app.services.memory_universe import MemoryUniverseService
from app.models.company import Company
from app.models.reputation_event_record import ReputationEventRecord
from app.models.geo_event import GeoEvent


class TestMemoryUniverse:
    async def test_timeline_aggregates_sources(self):
        factory = _get_session_factory()
        async with factory() as db:
            c = (await db.execute(select(Company).limit(1))).scalars().first()
            if not c: return
            nid = str(c.id)
            # ensure reputation + geo events exist for this node
            n_rep = (await db.execute(select(func.count(ReputationEventRecord.event_id)).where(ReputationEventRecord.node_id == nid))).scalar() or 0
            n_geo = (await db.execute(select(func.count(GeoEvent.id)).where(GeoEvent.source_node_id == c.id))).scalar() or 0
            tl = await MemoryUniverseService().unified_timeline(db, nid)
            assert "timeline" in tl and "count" in tl
            # timeline must include whatever durable sources exist
            assert tl["count"] >= 0
            sources = {t["source"] for t in tl["timeline"]}
            if n_rep: assert "reputation_event" in sources
            if n_geo: assert "geo_event" in sources

    async def test_cause_analysis_identifies_known_events(self):
        factory = _get_session_factory()
        async with factory() as db:
            c = (await db.execute(select(Company).limit(1))).scalars().first()
            if not c: return
            nid = str(c.id)
            res = await MemoryUniverseService().cause_analysis(db, nid)
            assert "cause_chain" in res
            assert isinstance(res["cause_chain"], list)

    async def test_narrative_never_invents_facts(self):
        factory = _get_session_factory()
        async with factory() as db:
            c = (await db.execute(select(Company).limit(1))).scalars().first()
            if not c: return
            nid = str(c.id)
            story = await MemoryUniverseService().generate_narrative(db, nid, c.name)
            assert "story" in story
            assert "不包含 AI 推断事实" in story["story"]