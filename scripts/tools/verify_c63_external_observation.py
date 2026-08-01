import asyncio, sys, uuid
sys.path.insert(0, r"D:\GEO-Industry-Engine\backend")
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.services.external_observation import ExternalObservationService
from app.models.observation import ObservationSource, ObservationArtifact
from app.models.capability import Capability
from app.universe.reputation_engine import get_reputation_engine, ReputationEngine
from app.universe.memory_engine import MemoryEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine

NODES = ["b4578afd-4454-4000-a4a3-8075d70d2f79", "3361adb3-0aef-451f-a834-fb9e0b8f29bb", "ed800951-9977-41a5-8ef4-6335d83fe2fc"]

async def main():
    ReputationEngine.reset(); MemoryEngine.reset(); RelationshipIntelligenceEngine.reset()
    factory = _get_session_factory()
    print("=" * 60); print("C6.3 FOUR SCENARIOS"); print("=" * 60)

    async with factory() as db:
        nid = NODES[0]
        # A: official website new capability description
        sid = "accept-a-" + uuid.uuid4().hex[:6]
        src = ObservationSource(source_id=sid, name="官网A", source_type="official_website", domain="a.example.com",
            base_url="https://a.example.com", trust_tier="high", node_id=nid, schedule_minutes=60,
            rate_limit_seconds=5, timeout_seconds=5, max_content_size=1000000, enabled=True)
        db.add(src); await db.commit()
        body = '<title>星辰AI发布AI Agent新能力</title><meta name="description" content="新增企业AI Agent开发能力">'
        async def fetch_a(source, url): return 200, {"content-type": "text/html"}, body.encode()
        svc = ExternalObservationService(fetch_fn=fetch_a, skip_network_validation=True)
        r = await svc.run_source(db, src, manual=True, actor_id="system")
        print(f"[A] run={r.status} candidates={r.candidates_found} change={r.change_created}")
        arts = (await db.execute(select(ObservationArtifact).where(ObservationArtifact.source_id == sid))).scalars().all()
        print(f"    artifact title: {arts[0].title if arts else None} hash={arts[0].content_hash[:8] if arts else ''}")

        # B: same page repeat -> NO_CHANGE
        r2 = await svc.run_source(db, src, manual=True, actor_id="system")
        count = (await db.execute(select(func.count(ObservationArtifact.id)).where(ObservationArtifact.source_id == sid))).scalar()
        print(f"[B] repeat run={r2.status} artifacts={count} (expect 1, NO_CHANGE)")

        # C: media report -> pending, reputation unchanged until verified
        nid2 = NODES[1]
        sid2 = "accept-c-" + uuid.uuid4().hex[:6]
        src2 = ObservationSource(source_id=sid2, name="媒体C", source_type="media", domain="c.example.com",
            base_url="https://c.example.com", trust_tier="medium", node_id=nid2, schedule_minutes=60,
            rate_limit_seconds=5, timeout_seconds=5, max_content_size=1000000, enabled=True)
        db.add(src2); await db.commit()
        body2 = "<title>权威媒体报道鼎新云计算获行业奖项</title>"
        async def fetch_c(source, url): return 200, {"content-type": "text/html"}, body2.encode()
        svc2 = ExternalObservationService(fetch_fn=fetch_c, skip_network_validation=True)
        rc = await svc2.run_source(db, src2, manual=True, actor_id="system")
        re = get_reputation_engine()
        rep_before = re.get_profile(nid2)
        print(f"[C] run={rc.status} candidates={rc.candidates_found} rep_before={rep_before.overall_score if rep_before else 0} (pending does not raise)")

    print("=" * 60); print("DONE"); print("=" * 60)

asyncio.run(main())
