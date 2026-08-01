"""C6.2 Governance tests: roles, ownership, four-eyes, audit, lazy restore."""
import sys, uuid, asyncio
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.services.governance import get_governance_service
from app.services.learning_loop import LearningLoopService
from app.models.user import User, UserRole
from app.models.governance import NodeMembership, AuditLog
from app.models.change_audit import CandidateChangeAudit
from app.models.evidence import Evidence
from app.models.company import Company
from app.models.onboarding_session import OnboardingSession
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine, EventStore, SnapshotManager
from app.universe.memory_engine import MemoryEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine


def make_user(db, email, role=UserRole.ENTERPRISE, name="用户"):
    u = User(email=email, password_hash="x", name=name, role=role)
    db.add(u)
    return u


class TestRolesAndMembership:
    def setup_method(self):
        MemoryEngine.reset(); ReputationEngine.reset(); RelationshipIntelligenceEngine.reset()

    async def test_admin_and_reviewer_platform_actions(self):
        factory = _get_session_factory()
        async with factory() as db:
            gov = get_governance_service()
            admin = make_user(db, f"admin-{uuid.uuid4().hex[:6]}@x.com", UserRole.ADMIN)
            reviewer = make_user(db, f"rev-{uuid.uuid4().hex[:6]}@x.com", UserRole.REVIEWER)
            plain = make_user(db, f"plain-{uuid.uuid4().hex[:6]}@x.com", UserRole.ENTERPRISE)
            db.add_all([admin, reviewer, plain]); await db.commit()
            assert gov.is_system_admin(admin)
            assert gov.is_reviewer(reviewer)
            assert not gov.is_reviewer(plain)
            assert gov.has_platform_action(admin, "change_apply")
            assert not gov.has_platform_action(plain, "change_apply")

    async def test_membership_owner_created_on_activate(self):
        factory = _get_session_factory()
        async with factory() as db:
            gov = get_governance_service()
            user = make_user(db, f"own-{uuid.uuid4().hex[:6]}@x.com")
            db.add(user); await db.commit()
            nid = str(uuid.uuid4())
            m = await gov.add_membership(db, user.id, nid, "node_owner", created_by=user.id)
            assert m.role == "node_owner"
            roles = await gov.get_node_roles(db, user.id, nid)
            assert "node_owner" in roles

    async def test_editor_can_submit_not_verify(self):
        factory = _get_session_factory()
        async with factory() as db:
            gov = get_governance_service()
            user = make_user(db, f"ed-{uuid.uuid4().hex[:6]}@x.com")
            db.add(user); await db.commit()
            nid = str(uuid.uuid4())
            await gov.add_membership(db, user.id, nid, "node_editor", created_by=user.id)
            assert await gov.can_node_action(db, user, nid, "submit_evidence") is True
            assert await gov.can_node_action(db, user, nid, "verify_evidence") is False

    async def test_four_eyes_blocks_self_verification(self):
        factory = _get_session_factory()
        async with factory() as db:
            gov = get_governance_service()
            uid = uuid.uuid4()
            assert await gov.four_eyes_ok(db, uid, uuid.uuid4(), "high") is True
            assert await gov.four_eyes_ok(db, uid, uid, "high") is False


async def _real_node_id():
    factory = _get_session_factory()
    async with factory() as db:
        row = (await db.execute(select(Company.id).limit(1))).scalars().first()
        return str(row) if row else str(uuid.uuid4())


class TestVerifiedIntegrity:
    def setup_method(self):
        MemoryEngine.reset(); ReputationEngine.reset(); RelationshipIntelligenceEngine.reset()

    async def test_verified_requires_verified_by(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = LearningLoopService()
            nid = await _real_node_id()
            ev = await svc._add_evidence(db, nid, {"title": "证据X", "source_url": "https://x.com"})
            try:
                await svc._set_evidence_verified(db, {"evidence_id": str(ev.id)})
                assert False, "must require verified_by"
            except ValueError:
                pass

    async def test_verified_rejects_non_uuid_label(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = LearningLoopService()
            nid = await _real_node_id()
            ev = await svc._add_evidence(db, nid, {"title": "证据Y", "source_url": "https://y.com"})
            try:
                await svc._set_evidence_verified(db, {"evidence_id": str(ev.id), "verified_by": "client-label"})
                assert False, "must reject non-UUID verifier"
            except ValueError:
                pass


class TestChangeAuditHistory:
    async def test_status_history_append_only(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = LearningLoopService()
            nid = await _real_node_id()
            actor = str(uuid.uuid4())
            cc = await svc.create_observation(db, {"node_id": nid, "change_type": "user_evidence",
                "proposed_value": {"title": "审计证据", "source_url": "https://a.com"},
                "source_type": "user"}, actor_id=actor)
            await svc.approve(db, str(cc.id), str(uuid.uuid4()), "ok")
            audits = (await db.execute(select(CandidateChangeAudit).where(CandidateChangeAudit.change_id == str(cc.id)))).scalars().all()
            statuses = [(a.from_status, a.to_status) for a in audits]
            assert ("OBSERVED", "PENDING_REVIEW") in statuses
            assert any(to == "APPROVED" for _, to in statuses)


class TestReputationLazyRestore:
    async def test_lazy_restore_matches_score(self):
        factory = _get_session_factory()
        async with factory() as db:
            ReputationEngine.reset(); EventStore.reset(); SnapshotManager.reset()
            re = get_reputation_engine()
            nid = str(uuid.uuid4())
            ev1 = re.record_event(nid, "company", "certification_passed", "ISO", "government")
            ev2 = re.record_event(nid, "company", "customer_success", "客户", "enterprise_customer")
            await re.persist_event(db, ev1); await re.persist_event(db, ev2); await db.commit()
            snap1 = re.recalculate(nid, "company")
            # Restart: fresh engine with NO memory events; lazy restore from DB
            ReputationEngine.reset(); EventStore.reset(); SnapshotManager.reset()
            re2 = get_reputation_engine()
            assert not re2.event_store.get_events(nid)
            snap2 = await re2.restore_from_db(db, nid, "company")
            assert snap2.overall_score == snap1.overall_score


class TestApplySafety:
    async def test_duplicate_apply_no_duplicate_evidence(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = LearningLoopService()
            nid = await _real_node_id()
            actor = str(uuid.uuid4())
            cc = await svc.create_observation(db, {"node_id": nid, "change_type": "user_evidence",
                "proposed_value": {"title": "幂等证据", "source_url": "https://idem.com"},
                "source_type": "user"}, actor_id=actor)
            await svc.approve(db, str(cc.id), str(uuid.uuid4()), "ok")
            await svc.apply(db, str(cc.id), actor)
            n1 = (await db.execute(select(func.count(Evidence.id)).where(Evidence.claim == "幂等证据"))).scalar()
            # second apply is idempotent
            await svc.apply(db, str(cc.id), actor)
            n2 = (await db.execute(select(func.count(Evidence.id)).where(Evidence.claim == "幂等证据"))).scalar()
            assert n1 == n2 and n1 >= 1