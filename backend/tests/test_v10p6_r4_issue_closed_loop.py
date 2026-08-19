"""V10.6-R4 issue closed-loop acceptance tests."""

import asyncio
import concurrent.futures
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import create_access_token
from app.database import _get_session_factory
from app.main import app
from app.models.company import Company
from app.models.entity import Entity
from app.models.evidence import Evidence
from app.models.geo_project import GeoProject, ProjectArtifact, ProjectWorkItem
from app.models.governance import AuditLog, NodeMembership
from app.models.intake import ClientIntake, IntakeAnalysis
from app.models.issue import IssueEvent, IssueRecord
from app.models.realm import RealmRegistry
from app.models.reputation import Reputation
from app.models.user import User, UserRole
from app.services.geo_project_service import get_geo_project_service
from app.services.governance import get_governance_service
from app.services.intake_service import get_intake_service
from app.services.issue_service import IssueStateError, get_issue_service
from app.services.project_plan_service import get_project_plan_service
from app.services.realm_service import get_realm_service


OWNER_TEMPLATE = {
    "phases": [{"phase": "阶段一", "tasks": [
        {"task_key": "t1", "title": "任务一", "purpose": "p", "description": "d", "expected_output": "o",
         "acceptance_criteria": "a", "required_materials": ["m"], "risks": ["r"], "execution_mode": "owner_review"},
    ]}]
}


def make_user(db, email, role=UserRole.ENTERPRISE):
    user = User(email=email, password_hash="x", name="域主", role=role)
    db.add(user)
    return user


async def _setup_realm(db, user, name):
    ws = await get_realm_service().create_enterprise(db, user, {
        "name": name,
        "website": f"https://{uuid.uuid4().hex[:8]}.test",
    })
    entity_id = uuid.UUID(ws["identity"]["id"])
    registry = (await db.execute(
        select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
    )).scalars().first()
    return entity_id, registry.id


async def _create_analyzed_intake(db, user, entity_id):
    svc = get_intake_service()
    intake = await svc.create_intake(db, user, str(entity_id), {
        "pasted_text": "品牌名称：R4品牌\n企业主体：R4企业\n产品：R4服务\n问题：建立GEO认知\n",
        "files": [],
    })
    await svc.analyze_intake(db, user, intake["id"])
    return intake["id"]


async def _create_project_with_task(db, owner, entity_id):
    svc = get_intake_service()
    intake_id = await _create_analyzed_intake(db, owner, entity_id)
    await svc.start_review(db, owner, intake_id)
    await svc.update_profile(db, owner, intake_id, {"target_customer": "R4客户"})
    await svc.confirm_profile(db, owner, intake_id)
    pos = await svc.generate_positioning(db, owner, intake_id)
    await svc.confirm_positioning(db, owner, intake_id, {"priority_direction": "先补齐行业赛道"}, expected_version=pos["version"])
    project = await get_geo_project_service().create_project_from_positioning(db, owner, intake_id, confirmed=True)
    await get_project_plan_service().generate_plan(db, owner, project["id"], "owner_defined", "owner-defined", OWNER_TEMPLATE)
    view = await get_project_plan_service().confirm_plan(db, owner, project["id"], True, 1)
    return project, intake_id, view["tasks"][0]


async def _cleanup(db, entity_ids, user_ids, intake_ids=(), project_ids=()):
    for pid in project_ids:
        await db.execute(delete(ProjectWorkItem).where(ProjectWorkItem.project_id == pid))
        await db.execute(delete(ProjectArtifact).where(ProjectArtifact.project_id == pid))
        await db.execute(delete(GeoProject).where(GeoProject.id == pid))
    for intake_id in intake_ids:
        await db.execute(delete(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake_id))
        await db.execute(delete(ClientIntake).where(ClientIntake.id == intake_id))
    for entity_id in entity_ids:
        registry = (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
        )).scalars().first()
        if registry:
            issues = (await db.execute(select(IssueRecord).where(IssueRecord.realm_id == registry.id))).scalars().all()
            for issue in issues:
                await db.execute(delete(IssueEvent).where(IssueEvent.issue_id == issue.id))
                await db.execute(delete(IssueRecord).where(IssueRecord.id == issue.id))
            await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == entity_id))
        await db.execute(delete(Evidence).where(Evidence.entity_id == entity_id))
        await db.execute(delete(Reputation).where(Reputation.node_id == entity_id))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(entity_id)))
        await db.execute(delete(Company).where(Company.id == entity_id))
        await db.execute(delete(Entity).where(Entity.id == entity_id))
    for user_id in user_ids:
        await db.execute(delete(User).where(User.id == user_id))
    await db.commit()


class TestIssueClosedLoop:
    async def test_manual_create_issue(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-manual-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "手动问题域")
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {
                    "original_text": "审批时权限不足",
                    "idempotency_key": f"manual-{uuid.uuid4().hex[:8]}",
                })
                assert issue["status"] == "open"
                assert issue["version"] == 1
                assert issue["ai_classification"]["engine"] == "rule_based"
                assert issue["ai_classification"]["truth_scope"] == "inferred"
                assert issue["permissions"]["can_triage"] is True
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_create_from_plan_task(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-task-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "任务问题域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {
                    "original_text": "工具执行失败",
                    "project_id": project["id"],
                    "work_item_id": task["id"],
                })
                assert issue["project_id"] == project["id"]
                assert issue["work_item_id"] == task["id"]
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_reject_non_plan_task(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-nontask-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "非计划任务域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, _ = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                other = ProjectWorkItem(
                    project_id=uuid.UUID(project["id"]),
                    work_type="other",
                    title="其他工作项",
                    status="planned",
                    truth_status="observed",
                )
                db.add(other)
                await db.commit()
                await db.refresh(other)
                with pytest.raises(ValueError, match="plan_task"):
                    await get_issue_service().create_issue(db, owner, str(registry_id), {
                        "original_text": "错误来源",
                        "project_id": project["id"],
                        "work_item_id": str(other.id),
                    })
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_reject_cross_realm_project(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-cross-{uuid.uuid4().hex[:8]}@x.com")
            other = make_user(db, f"r4-cross2-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, other])
            await db.commit()
            await db.refresh(owner)
            entity_a, registry_a = await _setup_realm(db, owner, "问题域A")
            entity_b, registry_b = await _setup_realm(db, other, "问题域B")
            try:
                project, intake_id, _ = await _create_project_with_task(db, other, entity_b)
                with pytest.raises(ValueError, match="does not belong"):
                    await get_issue_service().create_issue(db, owner, str(registry_a), {
                        "original_text": "跨域",
                        "project_id": project["id"],
                    })
                await _cleanup(db, [entity_a, entity_b], [owner.id, other.id], [uuid.UUID(intake_id)], [uuid.UUID(project["id"])])
            finally:
                pass

    async def test_idempotent_create(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-idem-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "幂等域")
            try:
                key = f"idem-{uuid.uuid4().hex[:8]}"
                first = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "重复", "idempotency_key": key})
                second = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "重复", "idempotency_key": key})
                assert first["id"] == second["id"]
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_invalid_state_transition(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-state-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "状态域")
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "越级"})
                with pytest.raises(IssueStateError):
                    await get_issue_service().update_issue(db, owner, issue["id"], {"status": "resolved"}, expected_version=1)
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_terminal_not_modifiable(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-term-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "终态域")
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "终态"})
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                await svc.update_issue(db, owner, issue["id"], {"status": "cancelled"}, expected_version=3)
                with pytest.raises(IssueStateError):
                    await svc.update_issue(db, owner, issue["id"], {"title": "改"}, expected_version=4)
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_resolved_back_to_in_progress(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-reopen-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "驳回域")
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "驳回"})
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=3)
                reopened = await svc.update_issue(db, owner, resolved["id"], {"status": "in_progress"}, expected_version=4)
                assert reopened["status"] == "in_progress"
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_verify_requires_owner(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-verify-{uuid.uuid4().hex[:8]}@x.com")
            editor = make_user(db, f"r4-verify-editor-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, editor])
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "验证权限域")
            await get_governance_service().add_membership(db, editor.id, str(entity_id), "node_editor", "company", owner.id)
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "验证"})
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=3)
                with pytest.raises(PermissionError, match="realm owner"):
                    await svc.verify_issue(db, editor, resolved["id"], expected_version=4)
            finally:
                await _cleanup(db, [entity_id], [owner.id, editor.id])

    async def test_version_conflict(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-ver-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "版本冲突域")
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "版本"})
                with pytest.raises(ValueError, match="版本已变化"):
                    await svc.update_issue(db, owner, issue["id"], {"title": "旧"}, expected_version=99)
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_concurrent_update_only_one_succeeds(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-con-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "并发域")
            entity_id_uuid = entity_id
            owner_id = owner.id
            owner_email = owner.email
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "并发"})
                issue_id = issue["id"]

                def worker(label):
                    async def inner():
                        engine = create_async_engine(settings.DATABASE_URL)
                        local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                        try:
                            async with local() as session:
                                actor = User(id=owner_id, email=owner_email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
                                try:
                                    await get_issue_service().update_issue(session, actor, issue_id, {"status": "triaged"}, expected_version=1)
                                    return ("ok", label)
                                except Exception as exc:
                                    return ("error", type(exc).__name__, str(exc))
                        finally:
                            await engine.dispose()
                    return asyncio.run(inner())

                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(worker, "A"), pool.submit(worker, "B")]
                    results = [f.result(timeout=30) for f in futures]
                assert len([r for r in results if r[0] == "ok"]) == 1
            finally:
                await _cleanup(db, [entity_id_uuid], [owner_id])

    async def test_attempt_history_append_unique(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-attempt-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "处理历史域")
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "处理"})
                after = await svc.add_attempt(db, owner, issue["id"], {"method": "方法A", "result": "failed"}, expected_version=1)
                after2 = await svc.add_attempt(db, owner, after["id"], {"method": "方法B", "result": "success"}, expected_version=2)
                attempts = [e for e in after2["events"] if e["event_type"] == "attempt"]
                assert len(attempts) == 2
                versions = [e["event_version"] for e in after2["events"]]
                assert len(versions) == len(set(versions))
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_commit_failure_rolls_back(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-roll-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "回滚域")
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "回滚"})
                owner_id = owner.id
                owner_email = owner.email
                with patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new=AsyncMock(side_effect=RuntimeError("injected"))):
                    with pytest.raises(RuntimeError):
                        await get_issue_service().update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                actor = User(id=owner_id, email=owner_email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
                after = await get_issue_service().get_issue(db, actor, issue["id"])
                assert after["status"] == "open"
                assert after["version"] == 1
            finally:
                await _cleanup(db, [entity_id], [owner_id])

    async def test_ai_suggestion_is_inferred_rule_based(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-ai-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "AI边界域")
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "文档权限不足"})
                assert issue["ai_classification"]["engine"] == "rule_based"
                assert issue["ai_classification"]["truth_scope"] == "inferred"
                assert issue["category"] is None
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_unverified_issue_cannot_generate_skill(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-skill-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "Skill域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {
                    "original_text": "未验证",
                    "project_id": project["id"],
                    "work_item_id": task["id"],
                })
                with pytest.raises(ValueError, match="已验证"):
                    await get_issue_service().generate_skill(db, owner, [issue["id"]])
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_cross_realm_idempotency_scope(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f-idem-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_a, registry_a = await _setup_realm(db, owner, "幂等域A")
            entity_b, registry_b = await _setup_realm(db, owner, "幂等域B")
            try:
                key = f"same-key-{uuid.uuid4().hex[:8]}"
                issue_a = await get_issue_service().create_issue(db, owner, str(registry_a), {"original_text": "A", "idempotency_key": key})
                issue_b = await get_issue_service().create_issue(db, owner, str(registry_b), {"original_text": "B", "idempotency_key": key})
                assert issue_a["id"] != issue_b["id"]
                assert issue_a["realm_id"] != issue_b["realm_id"]
            finally:
                await _cleanup(db, [entity_a, entity_b], [owner.id])

    async def test_patch_cannot_verify(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f-patch-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "PATCH域")
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "不能PATCH verified"})
                with pytest.raises(ValueError, match="专用验证接口"):
                    await get_issue_service().update_issue(db, owner, issue["id"], {"status": "verified"}, expected_version=1)
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_truth_scope_illegal_upgrade(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f-truth-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "truth域")
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "truth"})
                with pytest.raises(ValueError, match="truth_scope"):
                    await get_issue_service().update_issue(db, owner, issue["id"], {"truth_scope": "verified"}, expected_version=1)
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_classification_confirm_and_terminal(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f-class-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "分类域")
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "文档权限不足"})
                await svc.update_issue(db, owner, issue["id"], {"category": "权限与合规"}, expected_version=1)
                confirmed = await svc.confirm_classification(db, owner, issue["id"], expected_version=2)
                assert confirmed["classification_status"] == "confirmed"
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=3)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=4)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=5)
                verified = await svc.verify_issue(db, owner, resolved["id"], expected_version=6)
                with pytest.raises(IssueStateError, match="终态"):
                    await svc.classify_issue(db, owner, verified["id"], expected_version=7)
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_skill_sql_isolation_and_empty_issues(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f-skilliso-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_a, registry_a = await _setup_realm(db, owner, "Skill隔离A")
            entity_b, registry_b = await _setup_realm(db, owner, "Skill隔离B")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_a)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                issue = await get_issue_service().create_issue(db, owner, str(registry_a), {
                    "original_text": "验证后生成Skill",
                    "project_id": project["id"],
                    "work_item_id": task["id"],
                })
                await get_issue_service().update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await get_issue_service().update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                resolved = await get_issue_service().resolve_issue(db, owner, issue["id"], expected_version=3)
                verified = await get_issue_service().verify_issue(db, owner, resolved["id"], expected_version=4)
                await get_issue_service().generate_skill(db, owner, [verified["id"]])
                skills_a = await get_issue_service().list_skill_drafts(db, owner, str(registry_a))
                skills_b = await get_issue_service().list_skill_drafts(db, owner, str(registry_b))
                assert len(skills_a) == 1
                assert skills_b == []
                with pytest.raises(ValueError, match="不能为空"):
                    await get_issue_service().generate_skill(db, owner, [])
                await _cleanup(db, [entity_a, entity_b], [owner.id], intake_ids, project_ids)
            finally:
                pass

    async def test_skill_edit_version_conflict(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f-skilledit-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "Skill编辑域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {
                    "original_text": "编辑Skill",
                    "project_id": project["id"],
                    "work_item_id": task["id"],
                })
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=3)
                verified = await svc.verify_issue(db, owner, resolved["id"], expected_version=4)
                skill = await svc.generate_skill(db, owner, [verified["id"]])
                updated = await svc.update_skill_draft(db, owner, skill["id"], {"expected_output": "新输出"}, expected_version=1)
                assert updated["metadata_json"]["version"] == 2
                with pytest.raises(ValueError, match="版本已变化"):
                    await svc.update_skill_draft(db, owner, skill["id"], {"expected_output": "旧"}, expected_version=1)
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_cross_realm_skill_generation_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-skillcross-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_a, registry_a = await _setup_realm(db, owner, "Skill域A")
            entity_b, registry_b = await _setup_realm(db, owner, "Skill域B")
            try:
                issue_a = await get_issue_service().create_issue(db, owner, str(registry_a), {"original_text": "A"})
                issue_b = await get_issue_service().create_issue(db, owner, str(registry_b), {"original_text": "B"})
                with pytest.raises(ValueError, match="跨 Realm"):
                    await get_issue_service().generate_skill(db, owner, [issue_a["id"], issue_b["id"]])
                await _cleanup(db, [entity_a, entity_b], [owner.id])
            finally:
                pass

    async def test_skill_draft_not_activated_without_confirm(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-skillconf-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "Skill确认域")
            intake_ids, project_ids = [], []
            try:
                svc = get_issue_service()
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                issue = await svc.create_issue(db, owner, str(registry_id), {
                    "original_text": "验证后Skill",
                    "project_id": project["id"],
                    "work_item_id": task["id"],
                })
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=3)
                verified = await svc.verify_issue(db, owner, resolved["id"], expected_version=4)
                skill = await svc.generate_skill(db, owner, [verified["id"]])
                assert skill["status"] == "draft"
                assert skill["metadata_json"]["owner_confirmed"] is False
                confirmed = await svc.confirm_skill(db, owner, skill["id"], True)
                assert confirmed["status"] == "confirmed"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_cross_realm_api_404(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4-api-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"r4-apiout-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "API隔离域")
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "隔离"})
                owner_token = create_access_token(owner.id)
                outsider_token = create_access_token(outsider.id)
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    for method, path, body in [
                        ("GET", f"/api/v1/issues/{issue['id']}", None),
                        ("PATCH", f"/api/v1/issues/{issue['id']}", {"expected_version": 1, "title": "x"}),
                        ("POST", f"/api/v1/issues/{issue['id']}/attempts", {"method": "m", "expected_version": 1}),
                    ]:
                        out = await client.request(method, path, headers={"Authorization": f"Bearer {outsider_token}"}, json=body)
                        miss = await client.request(method, path.replace(issue["id"], str(uuid.uuid4())), headers={"Authorization": f"Bearer {owner_token}"}, json=body)
                        assert out.status_code == 404 and miss.status_code == 404
            finally:
                await _cleanup(db, [entity_id], [owner.id, outsider.id])

    async def test_api_patch_verified_blocked_and_empty_issues(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f-apiverify-{uuid.uuid4().hex[:8]}@x.com")
            editor = make_user(db, f"r4f-apieditor-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, editor])
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "API验证域")
            await get_governance_service().add_membership(db, editor.id, str(entity_id), "node_editor", "company", owner.id)
            try:
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "验证绕过"})
                editor_token = create_access_token(editor.id)
                owner_token = create_access_token(owner.id)
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    resp = await client.patch(
                        f"/api/v1/issues/{issue['id']}",
                        headers={"Authorization": f"Bearer {editor_token}"},
                        json={"status": "verified", "expected_version": 1},
                    )
                    assert resp.status_code == 400, resp.text
                    empty = await client.post(
                        f"/api/v1/issues/{issue['id']}/skills/generate",
                        headers={"Authorization": f"Bearer {owner_token}"},
                        json={"issue_ids": []},
                    )
                    assert empty.status_code == 400, empty.text
            finally:
                await _cleanup(db, [entity_id], [owner.id, editor.id])

    async def test_create_rejects_verified_truth_scope(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-truthcreate-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "truth创建域")
            try:
                with pytest.raises(ValueError, match="truth_scope"):
                    await get_issue_service().create_issue(db, owner, str(registry_id), {"original_text": "x", "truth_scope": "verified"})
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_idempotency_hash_fixed_length(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-idemlen-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "幂等长度域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                issue = await get_issue_service().create_issue(db, owner, str(registry_id), {
                    "original_text": "长度",
                    "project_id": project["id"],
                    "work_item_id": task["id"],
                    "idempotency_key": f"issue-{uuid.uuid4().hex[:8]}",
                })
                row = (await db.execute(select(IssueRecord).where(IssueRecord.id == uuid.UUID(issue["id"])))).scalars().first()
                assert row.idempotency_key and len(row.idempotency_key) == 64
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_skill_truth_status_inferred_and_attempt_content(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-skillcontent-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "Skill内容域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {
                    "original_text": "发布权限失败", "project_id": project["id"], "work_item_id": task["id"],
                })
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                await svc.add_attempt(db, owner, issue["id"], {"method": "方法A", "result": "failed", "failure_reason": "授权不足", "tool": "toolA"}, expected_version=3)
                await svc.add_attempt(db, owner, issue["id"], {"method": "方法B", "result": "success", "action": "重新授权", "tool": "toolB"}, expected_version=4)
                await svc.update_issue(db, owner, issue["id"], {"final_solution": "域主补授权后重试", "applicability_boundary": "仅限内部账号"}, expected_version=5)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=6)
                verified = await svc.verify_issue(db, owner, resolved["id"], expected_version=7)
                skill = await svc.generate_skill(db, owner, [verified["id"]])
                assert skill["truth_status"] == "inferred"
                content = skill["content_json"]
                assert content["truth_scope"] == "inferred"
                assert set(content["tools"]) == {"toolA", "toolB"}
                assert any(step.get("tool") == "toolB" for step in content["steps"])
                assert any(failure.get("failure") == "授权不足" for failure in content["common_failures"])
                assert content["expected_output"] == "域主补授权后重试"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_skill_edit_whitelist_and_only_draft(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-skilledit-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "Skill编辑域2")
            intake_ids, project_ids = [], []
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {
                    "original_text": "编辑边界", "project_id": project["id"], "work_item_id": task["id"],
                })
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=3)
                verified = await svc.verify_issue(db, owner, resolved["id"], expected_version=4)
                skill = await svc.generate_skill(db, owner, [verified["id"]])
                with pytest.raises(ValueError, match="禁止修改"):
                    await svc.update_skill_draft(db, owner, skill["id"], {"owner_confirmed": True}, expected_version=1)
                updated = await svc.update_skill_draft(db, owner, skill["id"], {"expected_output": "新方案"}, expected_version=1)
                assert updated["metadata_json"]["owner_confirmed"] is False
                confirmed = await svc.confirm_skill(db, owner, skill["id"], True)
                assert confirmed["status"] == "confirmed"
                with pytest.raises(IssueStateError, match="draft"):
                    await svc.update_skill_draft(db, owner, skill["id"], {"expected_output": "再改"}, expected_version=2)
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_classification_confirm_terminal_and_category(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-classconf-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "分类确认域2")
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "无分类"})
                with pytest.raises(ValueError, match="category"):
                    await svc.confirm_classification(db, owner, issue["id"], expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"category": "权限与合规"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=2)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=3)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=4)
                verified = await svc.verify_issue(db, owner, resolved["id"], expected_version=5)
                with pytest.raises(IssueStateError, match="终态"):
                    await svc.confirm_classification(db, owner, verified["id"], expected_version=6)
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_api_create_rejects_verified_truth_scope(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-apicreate-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "API创建truth域")
            try:
                token = create_access_token(owner.id)
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    resp = await client.post(
                        "/api/v1/issues",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"realm_id": str(registry_id), "original_text": "x", "truth_scope": "verified"},
                    )
                    assert resp.status_code == 400, resp.text
                    assert "observed" in resp.text
            finally:
                await _cleanup(db, [entity_id], [owner.id])

    async def test_classification_confirm_requires_owner_or_reviewer(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-classrole-{uuid.uuid4().hex[:8]}@x.com")
            editor = make_user(db, f"r4f2-classeditor-{uuid.uuid4().hex[:8]}@x.com", role=UserRole.ENTERPRISE)
            reviewer = make_user(db, f"r4f2-classreview-{uuid.uuid4().hex[:8]}@x.com", role=UserRole.REVIEWER)
            db.add_all([owner, editor, reviewer])
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "分类角色域")
            await get_governance_service().add_membership(db, editor.id, str(entity_id), "node_editor", "company", owner.id)
            await get_governance_service().add_membership(db, reviewer.id, str(entity_id), "node_reviewer", "company", owner.id)
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {"original_text": "分类角色"})
                await svc.update_issue(db, owner, issue["id"], {"category": "权限与合规"}, expected_version=1)
                with pytest.raises(PermissionError, match="专业审核"):
                    await svc.confirm_classification(db, editor, issue["id"], expected_version=2)
                confirmed = await svc.confirm_classification(db, reviewer, issue["id"], expected_version=2)
                assert confirmed["classification_status"] == "confirmed"
            finally:
                await _cleanup(db, [entity_id], [owner.id, editor.id, reviewer.id])

    async def test_skill_edit_concurrent_only_one_succeeds(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r4f2-skillconc-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, registry_id = await _setup_realm(db, owner, "Skill并发域")
            intake_ids, project_ids = [], []
            owner_id = owner.id
            owner_email = owner.email
            try:
                project, intake_id, task = await _create_project_with_task(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                svc = get_issue_service()
                issue = await svc.create_issue(db, owner, str(registry_id), {
                    "original_text": "并发编辑Skill", "project_id": project["id"], "work_item_id": task["id"],
                })
                await svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
                await svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
                resolved = await svc.resolve_issue(db, owner, issue["id"], expected_version=3)
                verified = await svc.verify_issue(db, owner, resolved["id"], expected_version=4)
                skill = await svc.generate_skill(db, owner, [verified["id"]])
                artifact_id = skill["id"]

                def worker(label):
                    async def inner():
                        engine = create_async_engine(settings.DATABASE_URL)
                        local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                        try:
                            async with local() as session:
                                actor = User(id=owner_id, email=owner_email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
                                try:
                                    await get_issue_service().update_skill_draft(
                                        session, actor, artifact_id, {"expected_output": f"方案{label}"}, expected_version=1,
                                    )
                                    return ("ok", label)
                                except Exception as exc:
                                    return ("error", type(exc).__name__, str(exc))
                        finally:
                            await engine.dispose()
                    return asyncio.run(inner())

                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(worker, "A"), pool.submit(worker, "B")]
                    results = [f.result(timeout=30) for f in futures]
                assert len([r for r in results if r[0] == "ok"]) == 1
                assert any("版本已变化" in str(r) for r in results if r[0] == "error")
            finally:
                await _cleanup(db, [entity_id], [owner_id], intake_ids, project_ids)
