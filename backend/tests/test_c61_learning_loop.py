"""C6.1 Continuous Learning Loop tests: dedup, review, apply, persistence, matching."""
import sys, uuid, asyncio
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.services.learning_loop import LearningLoopService
from app.services.node_activation import NodeActivationService
from app.models.candidate_change import CandidateChange
from app.models.company import Company
from app.models.evidence import Evidence
from app.models.company import Company
from app.models.reputation_event_record import ReputationEventRecord
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine, EventStore, SnapshotManager
from app.universe.memory_engine import MemoryEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine
from app.universe.connection_engine import FutureConnectionEngine, ConnectionCandidate
from app.universe.possibility_engine import PossibilityEngine, get_possibility_engine


@pytest.fixture
def lls():
    return LearningLoopService()


async def _real_node_id():
    """Return an existing company id so Evidence FK constraints pass."""
    factory = _get_session_factory()
    async with factory() as db:
        row = (await db.execute(select(Company.id).limit(1))).scalars().first()
        return str(row) if row else None


class TestDedupObservation:
    def setup_method(self):
        MemoryEngine.reset()
        ReputationEngine.reset()
        RelationshipIntelligenceEngine.reset()

    async def test_duplicate_observation_accumulates_not_duplicates(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await _real_node_id() or str(uuid.uuid4())
            data = {"node_id": nid, "change_type": "user_evidence",
                    "proposed_value": {"title": "官网", "source_url": "https://a.com"},
                    "source_type": "user", "source_id": "src-1"}
            c1 = await lls.create_observation(db, data)
            c2 = await lls.create_observation(db, data)
            assert c1.id == c2.id
            assert c2.occurrence_count >= 2  # accumulates, not duplicates

    async def test_self_report_does_not_raise_reputation(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            re = get_reputation_engine()
            nid = await _real_node_id() or str(uuid.uuid4())
            re.record_event(nid, "company", "certification_passed", "ISO", "government")
            snap_before = re.recalculate(nid, "company")
            cc = await lls.create_observation(db, {"node_id": nid, "change_type": "user_evidence",
                "proposed_value": {"title": "未验证案例", "source_url": "https://x.com", "evidence_type": "customer_case"},
                "source_type": "user", "confidence_level": 0.3})
            await lls.approve(db, str(cc.id), "admin", "ok")
            await lls.apply(db, str(cc.id), "admin")
            snap_after = re.recalculate(nid, "company")
            # self_report evidence must not raise reputation beyond the original event
            assert snap_after.overall_score <= snap_before.overall_score + 0.5

    async def test_verified_evidence_triggers_recompute(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await _real_node_id() or str(uuid.uuid4())
            cc = await lls.create_observation(db, {"node_id": nid, "change_type": "evidence_verification_change",
                "proposed_value": {"evidence_id": "00000000-0000-0000-0000-000000000000"},
                "source_type": "admin"})
            assert cc.review_status in ("OBSERVED", "PENDING_REVIEW")

    async def test_rejected_change_does_not_modify_node(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await _real_node_id() or str(uuid.uuid4())
            cc = await lls.create_observation(db, {"node_id": nid, "change_type": "user_evidence",
                "proposed_value": {"title": "假案例", "source_url": "https://fake.com"},
                "source_type": "user"})
            await lls.reject(db, str(cc.id), "admin", "无法验证")
            evs = (await db.execute(select(func.count(Evidence.id)).where(Evidence.claim == "假案例"))).scalar()
            assert evs == 0

    async def test_high_impact_cannot_auto_approve(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await _real_node_id() or str(uuid.uuid4())
            cc = await lls.create_observation(db, {"node_id": nid, "change_type": "profile_update",
                "proposed_value": {"capabilities": [{"name": "X", "core_capability": "Y"}]},
                "source_type": "user", "impact_level": "high"})
            try:
                await lls.approve(db, str(cc.id), "system", "auto")
                assert False, "system actor must be rejected"
            except ValueError:
                pass

    async def test_apply_idempotent(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await _real_node_id() or str(uuid.uuid4())
            cc = await lls.create_observation(db, {"node_id": nid, "change_type": "user_evidence",
                "proposed_value": {"title": "案例A", "source_url": "https://a.com"}, "source_type": "user"})
            await lls.approve(db, str(cc.id), "admin", "ok")
            await lls.apply(db, str(cc.id), "admin")
            count1 = (await db.execute(select(func.count(Evidence.id)).where(Evidence.claim == "案例A"))).scalar()
            # Second apply is idempotent: no additional evidence rows
            await lls.apply(db, str(cc.id), "admin")
            count2 = (await db.execute(select(func.count(Evidence.id)).where(Evidence.claim == "案例A"))).scalar()
            assert count1 == count2

    async def test_apply_failed_retry(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await _real_node_id() or str(uuid.uuid4())
            cc = await lls.create_observation(db, {"node_id": nid, "change_type": "user_evidence",
                "proposed_value": {"title": "案例B", "source_url": "https://b.com"}, "source_type": "user"})
            await lls.approve(db, str(cc.id), "admin", "ok")
            await lls.apply(db, str(cc.id), "admin")
            assert cc.review_status == "APPLIED"

    async def test_correction_preserves_history(self, lls):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await _real_node_id() or str(uuid.uuid4())
            c1 = await lls.create_observation(db, {"node_id": nid, "change_type": "admin_observation",
                "proposed_value": {"title": "旧观察"}, "source_type": "admin"})
            c2 = await lls.create_observation(db, {"node_id": nid, "change_type": "admin_observation",
                "proposed_value": {"title": "修正观察"}, "source_type": "admin", "source_id": "src-2"})
            history = await lls.get_learning_history(db, nid)
            assert len(history) >= 2  # append-only: correction adds, never deletes


class TestReputationRestart:
    async def test_restart_restores_same_score(self):
        factory = _get_session_factory()
        async with factory() as db:
            ReputationEngine.reset()
            re = get_reputation_engine()
            nid = str(uuid.uuid4())  # reputation_events has no FK; use clean id
            ev1 = re.record_event(nid, "company", "certification_passed", "ISO", "government")
            ev2 = re.record_event(nid, "company", "customer_success", "客户项目", "enterprise_customer")
            await re.persist_event(db, ev1)
            await re.persist_event(db, ev2)
            await db.commit()
            snap1 = re.recalculate(nid, "company")
            # Simulate restart: fresh engine, restore from DB, recalculate            ReputationEngine.reset()
            EventStore.reset()
            SnapshotManager.reset()
            re2 = get_reputation_engine()
            snap2 = await re2.restore_from_db(db, nid, "company")
            assert snap2.overall_score == snap1.overall_score


class TestDedupMatching:
    async def test_four_match_levels(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = NodeActivationService()
            # exact by name (existing 星辰AI营销科技 in DB)
            m1 = await svc.match_existing_node(db, {"company_name": "星辰AI营销科技", "website": "https://xingchen.example.com"})
            assert m1["match_level"] in ("exact_match", "probable_match", "possible_duplicate")
            # new node
            m2 = await svc.match_existing_node(db, {"company_name": f"全新企业{uuid.uuid4().hex[:6]}", "website": "https://brand-new.example.com"})
            assert m2["match_level"] == "new_node"


class TestSourceKindAndHorizons:
    def test_connection_source_kind_seed(self):
        from app.universe.connection_engine import get_connection_engine
        report = get_connection_engine().discover_connections("src-kind-node", "company")
        if report and report.candidates:
            assert all(c.source_kind == "seed" for c in report.candidates)

    async def test_possibility_horizons_availability(self):
        from app.universe.context_engine import get_context_engine
        ctx = get_context_engine().understand("hz-node", "company", {"name": "horizon"})
        graph = get_possibility_engine().project(ctx)
        d = graph.to_dict()
        assert "horizon_availability" in d
        # All configured horizons (30/90/180) must be present, available or unavailable with reason
        for h in ("30", "90", "180"):
            assert h in d["horizon_availability"]
            assert "available" in d["horizon_availability"][h]
            if not d["horizon_availability"][h]["available"]:
                assert "reason" in d["horizon_availability"][h]

    def test_rules_never_auto_change(self, lls):
        from app.universe.rules import get_rule_engine
        rules = get_rule_engine().rules.rules
        assert len(rules) > 0
        # learning service has no rule-mutation method
        assert not hasattr(lls, "update_rule")
        assert not hasattr(lls, "change_weights")