"""C6.5-R: reputation fact boundary, synthetic transaction closure, unverified snapshot marking."""
import sys, uuid
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

from sqlalchemy import select
from app.database import _get_session_factory
from app.services.node_activation import NodeActivationService
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine
from app.universe.memory_engine import MemoryEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine


class TestReputationFactBoundary:
    def setup_method(self):
        ReputationEngine.reset(); MemoryEngine.reset(); RelationshipIntelligenceEngine.reset()

    async def test_observed_evidence_does_not_raise_reputation(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = NodeActivationService()
            nid = str(uuid.uuid4())
            re = get_reputation_engine()
            class FakeCompany:
                id = uuid.UUID(nid)
            await svc._compute_reputation(db, FakeCompany(), {"evidence_items": [
                {"evidence_type": "media_report", "title": "公开报道", "claim": "x", "truth_status": "observed"}]})
            assert re.event_store.get_events(nid) == []

    async def test_verified_evidence_raises_reputation(self):
        from app.models.evidence import Evidence
        from app.models.entity import Entity
        factory = _get_session_factory()
        async with factory() as db:
            svc = NodeActivationService()
            re = get_reputation_engine()
            nid = str(uuid.uuid4())
            # verified evidence should produce a reputation event (association source)
            # call _compute_reputation with a fake company carrying id
            class FakeCompany:
                id = uuid.UUID(nid)
            await svc._compute_reputation(db, FakeCompany(), {"evidence_items": [
                {"evidence_type": "award_certification", "title": "认证", "claim": "cert", "truth_status": "verified"}]})
            events = re.event_store.get_events(nid)
            assert len(events) >= 1, "verified evidence must create reputation event"

    async def test_synthetic_never_affects_real_reputation(self):
        from app.models.evidence import Evidence
        factory = _get_session_factory()
        async with factory() as db:
            svc = NodeActivationService()
            re = get_reputation_engine()
            nid = str(uuid.uuid4())
            class FakeCompany:
                id = uuid.UUID(nid)
            await svc._compute_reputation(db, FakeCompany(), {"evidence_items": [
                {"evidence_type": "media_report", "title": "仿真", "claim": "s", "truth_status": "synthetic", "is_synthetic": True}]})
            assert re.event_store.get_events(nid) == []


class TestSandboxTransactions:
    async def test_transaction_closure_and_idempotency(self):
        from app.models.company import Company
        from app.universe.transaction_engine import get_transaction_engine, TransactionEngine
        TransactionEngine.reset()
        factory = _get_session_factory()
        async with factory() as db:
            engine = get_transaction_engine()
            syn = (await db.execute(select(Company).where(Company.name.like("%仿真%")))).scalars().all()
            if len(syn) < 2:
                # create two synthetic companies for the test
                from app.models.company import Company as C
                from app.models.entity import Entity
                a = C(name="交易仿真A（仿真）", entity_type="company", geo_id="GEO-COMP-TEST-A", description="test")
                b = C(name="交易仿真B（仿真）", entity_type="company", geo_id="GEO-COMP-TEST-B", description="test")
                db.add_all([a, b]); await db.commit()
                syn = [a, b]
            a, b = syn[0], syn[1]
            tx = engine.propose(str(a.id), str(b.id), {"category": "service", "title": "仿真交易", "timeline_days": 30})
            engine.transition(tx.transaction_id, "agreed", str(a.id))
            engine.transition(tx.transaction_id, "started", str(b.id))
            outcome = engine.complete(tx.transaction_id, "settled", actor_id=str(a.id))
            assert outcome.status == "settled"
            hist = engine.get_transaction_with_history(tx.transaction_id)
            before = len(hist["events"])
            try:
                engine.complete(tx.transaction_id, "settled", actor_id=str(a.id))
            except ValueError:
                pass
            after = len(engine.get_transaction_with_history(tx.transaction_id)["events"])
            assert before == after, "second complete must be idempotent"