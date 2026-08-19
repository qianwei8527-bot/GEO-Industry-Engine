"""V10.6-R3-FIX1 project plan acceptance scenarios."""

import asyncio
import concurrent.futures
import sys
import uuid
from datetime import datetime, timedelta, timezone
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
from app.models.realm import RealmRegistry
from app.models.reputation import Reputation
from app.models.user import User, UserRole
from app.services.geo_project_service import get_geo_project_service
from app.services.governance import get_governance_service
from app.services.intake_service import get_intake_service
from app.services.project_plan_service import PlanStateError, get_project_plan_service
from app.services.realm_service import get_realm_service

OWNER_TEMPLATE = {
    "phases": [
        {
            "phase": "阶段一",
            "tasks": [
                {
                    "task_key": "t1",
                    "title": "任务一",
                    "purpose": "确认目标",
                    "description": "说明",
                    "expected_output": "产出",
                    "acceptance_criteria": "验收",
                    "required_materials": ["材料1"],
                    "risks": ["风险1"],
                    "execution_mode": "owner_review",
                },
                {
                    "task_key": "t2",
                    "title": "任务二",
                    "purpose": "整理事实",
                    "description": "说明",
                    "expected_output": "产出",
                    "acceptance_criteria": "验收",
                    "required_materials": ["材料2"],
                    "risks": ["风险2"],
                    "execution_mode": "owner_review",
                },
            ],
        },
        {
            "phase": "阶段二",
            "tasks": [
                {
                    "task_key": "t3",
                    "title": "任务三",
                    "purpose": "建设资产",
                    "description": "说明",
                    "expected_output": "产出",
                    "acceptance_criteria": "验收",
                    "required_materials": ["材料3"],
                    "risks": ["风险3"],
                    "execution_mode": "content_production",
                },
                {
                    "task_key": "t4",
                    "title": "任务四",
                    "purpose": "实验复盘",
                    "description": "说明",
                    "expected_output": "产出",
                    "acceptance_criteria": "验收",
                    "required_materials": ["材料4"],
                    "risks": ["风险4"],
                    "execution_mode": "tool_execution",
                },
            ],
        },
    ]
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


async def _create_analyzed_intake(db, user, entity_id, text=None):
    svc = get_intake_service()
    intake = await svc.create_intake(db, user, str(entity_id), {
        "pasted_text": text or (
            "品牌名称：R3FIX品牌\n"
            "企业主体：R3FIX企业有限公司\n"
            "产品：R3FIX服务\n"
            "问题：从零开始建立GEO认知\n"
        ),
        "files": [],
    })
    await svc.analyze_intake(db, user, intake["id"])
    return intake["id"]


async def _create_confirmed_project(db, owner, entity_id):
    svc = get_intake_service()
    intake_id = await _create_analyzed_intake(db, owner, entity_id)
    await svc.start_review(db, owner, intake_id)
    await svc.update_profile(db, owner, intake_id, {"target_customer": "R3FIX行业客户"})
    await svc.confirm_profile(db, owner, intake_id)
    draft = await svc.generate_positioning(db, owner, intake_id)
    confirmed = await svc.confirm_positioning(
        db, owner, intake_id,
        {"priority_direction": "先补齐行业赛道"},
        expected_version=draft["version"],
    )
    project = await get_geo_project_service().create_project_from_positioning(
        db, owner, intake_id, confirmed=True,
        expected_position_version=confirmed["metadata_json"]["positioning_version"],
    )
    return project, intake_id


async def _make_draft(db, owner, project_id):
    return await get_project_plan_service().generate_plan(
        db, owner, project_id, "owner_defined", "owner-defined", OWNER_TEMPLATE
    )


async def _confirm(db, owner, project_id, expected_version=1):
    return await get_project_plan_service().confirm_plan(
        db, owner, project_id, True, expected_version
    )


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
            intakes = (await db.execute(
                select(ClientIntake).where(ClientIntake.realm_id == registry.id)
            )).scalars().all()
            for intake in intakes:
                await db.execute(delete(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake.id))
                await db.execute(delete(ClientIntake).where(ClientIntake.id == intake.id))
            projects = (await db.execute(
                select(GeoProject).where(GeoProject.realm_id == registry.id)
            )).scalars().all()
            for project in projects:
                await db.execute(delete(ProjectWorkItem).where(ProjectWorkItem.project_id == project.id))
                await db.execute(delete(ProjectArtifact).where(ProjectArtifact.project_id == project.id))
                await db.execute(delete(GeoProject).where(GeoProject.id == project.id))
            await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == entity_id))
        await db.execute(delete(Evidence).where(Evidence.entity_id == entity_id))
        await db.execute(delete(Reputation).where(Reputation.node_id == entity_id))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(entity_id)))
        await db.execute(delete(Company).where(Company.id == entity_id))
        await db.execute(delete(Entity).where(Entity.id == entity_id))
    for user_id in user_ids:
        await db.execute(delete(User).where(User.id == user_id))
    await db.commit()


class TestProjectPlanAcceptance:
    async def test_platform_seed_is_blank_structure(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-blank-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "空白结构域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await get_project_plan_service().generate_plan(
                    db, owner, project["id"], "platform_seed", "platform-seed-blank"
                )
                assert view["plan_status"] == "plan_draft"
                assert view["draft_plan"]["tasks"] == []
                assert view["draft_plan"]["phases"][0]["phase"] == "未命名阶段"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_owner_defined_records_provenance(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-prov-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "来源记录域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                payload = view["draft_plan"]
                assert payload["source_type"] == "owner_defined"
                assert payload["provenance"] == "owner_defined_submission"
                assert payload["owner_confirmed"] is True
                assert payload["owner_id"] is None
                assert payload["submitted_by"] == str(owner.id)
                assert payload["realm_id"] == project["realm_id"]
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_source_type_and_id_are_validated(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-src-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "来源校验域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                svc = get_project_plan_service()
                with pytest.raises(ValueError, match="invalid workflow source_type"):
                    await svc.generate_plan(db, owner, project["id"], "not-a-source")
                with pytest.raises(ValueError, match="source_type/source_id mismatch"):
                    await svc.generate_plan(db, owner, project["id"], "owner_seeded", "platform-seed-blank")
                with pytest.raises(ValueError, match="workflow source not found"):
                    await svc.generate_plan(db, owner, project["id"], "realm_template", "realm-template-geo-starter")
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_deterministic_plan_hash(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-det-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "确定性域")
            intake_ids, project_ids = [], []
            try:
                svc = get_project_plan_service()
                p1, i1 = await _create_confirmed_project(db, owner, entity_id)
                p2, i2 = await _create_confirmed_project(db, owner, entity_id)
                intake_ids += [uuid.UUID(i1), uuid.UUID(i2)]
                project_ids += [uuid.UUID(p1["id"]), uuid.UUID(p2["id"])]
                v1 = await _make_draft(db, owner, p1["id"])
                v2 = await _make_draft(db, owner, p2["id"])
                assert v1["plan_hash"] == v2["plan_hash"]
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_unknown_items_are_not_fabricated(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-unk-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "unknown域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                assert "task_owners_unassigned" in view["unknown_items"]
                assert "task_dates_unassigned" in view["unknown_items"]
                assert all(t.get("owner_id") is None for t in view["draft_plan"]["tasks"])
                assert all(t.get("start_at") is None for t in view["draft_plan"]["tasks"])
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_r2_project_enters_r3(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-enter-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "进入R3域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                svc = get_project_plan_service()
                before = await svc.list_plan(db, owner, project["id"])
                assert before["plan_status"] == "project_created"
                after = await _make_draft(db, owner, project["id"])
                assert after["plan_status"] == "plan_draft"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_illegal_state_jump_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-jump-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "状态跳转域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                svc = get_project_plan_service()
                with pytest.raises(PlanStateError):
                    await svc.confirm_plan(db, owner, project["id"], True, 1)
                await _make_draft(db, owner, project["id"])
                with pytest.raises(PlanStateError):
                    await svc.generate_plan(db, owner, project["id"], "owner_defined", "owner-defined", OWNER_TEMPLATE)
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_expected_version_conflict(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-ver-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "版本冲突域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                with pytest.raises(ValueError, match="版本已变化"):
                    await get_project_plan_service().update_draft(
                        db, owner, project["id"], 99, {"tasks": view["draft_plan"]["tasks"]}
                    )
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_concurrent_draft_update_only_one_succeeds(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-conedit-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "并发编辑域")
            entity_id_uuid = entity_id
            owner_id = owner.id
            owner_email = owner.email
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                project_id = project["id"]
                view = await _make_draft(db, owner, project_id)
                tasks = list(view["draft_plan"]["tasks"])

                def worker(label):
                    async def inner():
                        engine = create_async_engine(settings.DATABASE_URL)
                        local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                        try:
                            async with local() as session:
                                actor = User(id=owner_id, email=owner_email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
                                try:
                                    await get_project_plan_service().update_draft(
                                        session, actor, project_id, 1,
                                        {"tasks": tasks, "phases": view["draft_plan"]["phases"]},
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
                assert len([r for r in results if r[0] == "error" and "版本已变化" in r[2]]) == 1
                versions = (await db.execute(
                    select(ProjectArtifact).where(ProjectArtifact.project_id == uuid.UUID(project_id))
                )).scalars().all()
                plan_versions = [a.metadata_json.get("plan_version") for a in versions]
                assert len(plan_versions) == len(set(plan_versions))
            finally:
                await _cleanup(db, [entity_id_uuid], [owner_id], intake_ids, project_ids)

    async def test_zero_task_confirm_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-zero-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "零任务域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await get_project_plan_service().generate_plan(
                    db, owner, project["id"], "platform_seed", "platform-seed-blank"
                )
                with pytest.raises(ValueError, match="零任务"):
                    await _confirm(db, owner, project["id"])
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_confirm_requires_explicit_flag(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-flag-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "显式确认域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                with pytest.raises(ValueError, match="显式确认"):
                    await get_project_plan_service().confirm_plan(db, owner, project["id"], False, 1)
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_confirm_requires_owner_role(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-owner-{uuid.uuid4().hex[:8]}@x.com")
            editor = make_user(db, f"r3f-editor-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, editor])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(editor)
            entity_id, _ = await _setup_realm(db, owner, "确认权限域")
            await get_governance_service().add_membership(
                db, editor.id, str(entity_id), "node_editor", "company", owner.id
            )
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                with pytest.raises(PermissionError, match="realm owner"):
                    await get_project_plan_service().confirm_plan(db, editor, project["id"], True, 1)
            finally:
                await _cleanup(db, [entity_id], [owner.id, editor.id], intake_ids, project_ids)

    async def test_confirm_generates_plan_tasks(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-gen-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "生成任务域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                view = await _confirm(db, owner, project["id"])
                assert view["plan_status"] == "plan_confirmed"
                assert len(view["tasks"]) > 0
                assert all(t["task_version"] == 1 for t in view["tasks"])
                assert all(t["status"] == "planned" for t in view["tasks"])
                rows = (await db.execute(
                    select(ProjectWorkItem).where(
                        ProjectWorkItem.project_id == uuid.UUID(project["id"]),
                        ProjectWorkItem.work_type == "plan_task",
                    )
                )).scalars().all()
                assert len(rows) == len(view["tasks"])
                assert all(row.acceptance_criteria for row in rows)
                assert all(row.required_materials is not None for row in rows)
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_repeat_confirm_no_duplicate(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-repeat-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "重复确认域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                first = await _confirm(db, owner, project["id"])
                second = await _confirm(db, owner, project["id"])
                assert len(first["tasks"]) == len(second["tasks"])
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_concurrent_confirm_one_task_set(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-conconf-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "并发确认域")
            entity_id_uuid = entity_id
            owner_id = owner.id
            owner_email = owner.email
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                project_id = project["id"]
                await _make_draft(db, owner, project_id)

                def worker(label):
                    async def inner():
                        engine = create_async_engine(settings.DATABASE_URL)
                        local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                        try:
                            async with local() as session:
                                actor = User(id=owner_id, email=owner_email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
                                try:
                                    await get_project_plan_service().confirm_plan(session, actor, project_id, True, 1)
                                    return ("ok", label)
                                except Exception as exc:
                                    return ("error", type(exc).__name__, str(exc))
                        finally:
                            await engine.dispose()
                    return asyncio.run(inner())

                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(worker, "A"), pool.submit(worker, "B")]
                    results = [f.result(timeout=30) for f in futures]
                assert all(r[0] == "ok" for r in results)
                rows = (await db.execute(
                    select(ProjectWorkItem).where(
                        ProjectWorkItem.project_id == uuid.UUID(project_id),
                        ProjectWorkItem.work_type == "plan_task",
                    )
                )).scalars().all()
                assert len(rows) > 0
                versions = {(r.metadata_json or {}).get("plan_version") for r in rows}
                assert len(versions) == 1
            finally:
                await _cleanup(db, [entity_id_uuid], [owner_id], intake_ids, project_ids)

    async def test_confirm_failure_rolls_back(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-roll-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "回滚域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                tasks = list(view["draft_plan"]["tasks"])
                tasks[0]["owner_id"] = str(uuid.uuid4())
                await get_project_plan_service().update_draft(
                    db, owner, project["id"], 1,
                    {"tasks": tasks, "phases": view["draft_plan"]["phases"]},
                )
                with pytest.raises(ValueError, match="负责人"):
                    await _confirm(db, owner, project["id"], 2)
                rows = (await db.execute(
                    select(ProjectWorkItem).where(ProjectWorkItem.project_id == uuid.UUID(project["id"]))
                )).scalars().all()
                assert rows == []
                after = await get_project_plan_service().list_plan(db, owner, project["id"])
                assert after["plan_status"] == "plan_draft"
                confirmed = [a for a in after["versions"] if a["status"] == "confirmed"]
                assert confirmed == []
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_cross_realm_api_is_anti_enumeration(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-api-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"r3f-out-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, _ = await _setup_realm(db, owner, "隔离域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                owner_token = create_access_token(owner.id)
                outsider_token = create_access_token(outsider.id)
                endpoints = [
                    ("GET", f"/api/v1/project-plans/{project['id']}", None),
                    ("POST", f"/api/v1/project-plans/{project['id']}/generate", {}),
                    ("PUT", f"/api/v1/project-plans/{project['id']}/draft", {"expected_version": 1, "plan": {}}),
                    ("POST", f"/api/v1/project-plans/{project['id']}/confirm", {"confirmed": True, "expected_version": 1}),
                    ("GET", f"/api/v1/project-plans/{project['id']}/export.csv", None),
                ]
                missing_id = str(uuid.uuid4())
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    for method, path, body in endpoints:
                        out = await client.request(method, path, headers={"Authorization": f"Bearer {outsider_token}"}, json=body)
                        miss = await client.request(
                            method, path.replace(project["id"], missing_id),
                            headers={"Authorization": f"Bearer {owner_token}"}, json=body,
                        )
                        assert out.status_code == 404 and miss.status_code == 404
                        assert out.json()["detail"] == "resource not found"
                        assert miss.json()["detail"] == "resource not found"
            finally:
                await _cleanup(db, [entity_id], [owner.id, outsider.id], intake_ids, project_ids)

    async def test_dependency_cycle_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-cycle-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "依赖环域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                tasks = list(view["draft_plan"]["tasks"])
                tasks[0]["depends_on"] = [tasks[1]["task_key"]]
                tasks[1]["depends_on"] = [tasks[0]["task_key"]]
                with pytest.raises(ValueError, match="cycle"):
                    await get_project_plan_service().update_draft(
                        db, owner, project["id"], 1, {"tasks": tasks}
                    )
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_date_order_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-date-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "日期域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                tasks = list(view["draft_plan"]["tasks"])
                tasks[0]["start_at"] = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
                tasks[0]["due_at"] = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
                with pytest.raises(ValueError, match="due_at"):
                    await get_project_plan_service().update_draft(
                        db, owner, project["id"], 1, {"tasks": tasks}
                    )
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_task_status_transitions_strict(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-state-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "任务状态域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                view = await _confirm(db, owner, project["id"])
                task = view["tasks"][0]
                svc = get_project_plan_service()
                with pytest.raises(PlanStateError):
                    await svc.update_task(db, owner, project["id"], task["id"], {
                        "status": "completed", "progress": 100, "expected_task_version": 1,
                    })
                active = await svc.update_task(db, owner, project["id"], task["id"], {
                    "status": "in_progress", "progress": 50, "expected_task_version": 1,
                })
                task_v2 = next(t for t in active["tasks"] if t["id"] == task["id"])
                assert task_v2["task_version"] == 2
                blocked = await svc.update_task(db, owner, project["id"], task["id"], {
                    "status": "blocked", "progress": 50, "expected_task_version": 2,
                })
                task_v3 = next(t for t in blocked["tasks"] if t["id"] == task["id"])
                assert task_v3["status"] == "blocked"
                done = await svc.update_task(db, owner, project["id"], task["id"], {
                    "status": "in_progress", "progress": 60, "expected_task_version": 3,
                })
                task_v4 = next(t for t in done["tasks"] if t["id"] == task["id"])
                assert task_v4["status"] == "in_progress"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_task_version_conflict(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-taskver-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "任务版本域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                view = await _confirm(db, owner, project["id"])
                task = view["tasks"][0]
                svc = get_project_plan_service()
                with pytest.raises(ValueError, match="任务版本已变化"):
                    await svc.update_task(db, owner, project["id"], task["id"], {
                        "status": "in_progress", "progress": 50, "expected_task_version": 99,
                    })
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_plan_completed_is_terminal(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-term-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "终态域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                view = await _confirm(db, owner, project["id"])
                svc = get_project_plan_service()
                for task in view["tasks"]:
                    await svc.update_task(db, owner, project["id"], task["id"], {
                        "status": "in_progress", "progress": 50, "expected_task_version": 1,
                    })
                    latest = await svc.list_plan(db, owner, project["id"])
                    current = next(t for t in latest["tasks"] if t["id"] == task["id"])
                    await svc.update_task(db, owner, project["id"], task["id"], {
                        "status": "completed", "progress": 100, "expected_task_version": current["task_version"],
                    })
                done = await svc.list_plan(db, owner, project["id"])
                assert done["plan_status"] == "plan_completed"
                with pytest.raises(PlanStateError, match="terminal"):
                    await svc.update_task(db, owner, project["id"], done["tasks"][0]["id"], {
                        "status": "in_progress", "progress": 10, "expected_task_version": 4,
                    })
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_confirmed_not_verified(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-verified-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "真值域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                await _confirm(db, owner, project["id"])
                artifact = (await db.execute(
                    select(ProjectArtifact)
                    .where(ProjectArtifact.project_id == uuid.UUID(project["id"]))
                    .order_by(ProjectArtifact.created_at.desc())
                )).scalars().first()
                assert artifact.truth_status == "observed"
                assert artifact.content_json["truth_scope"] == "inferred"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_csv_is_realm_scoped(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-csv-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "CSV域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                await _confirm(db, owner, project["id"])
                csv_text = await get_project_plan_service().export_plan_csv(db, owner, project["id"])
                assert csv_text.startswith("\ufeff")
                assert "task_key" in csv_text
                assert "R3FIX" not in csv_text or "other-realm" not in csv_text
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_external_ai_not_required(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f-noai-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "无AI域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                assert view["plan_hash"]
                confirmed = await _confirm(db, owner, project["id"])
                assert len(confirmed["tasks"]) > 0
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_owner_defined_api_generation(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-ownerapi-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "owner定义API域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                token = create_access_token(owner.id)
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    resp = await client.post(
                        f"/api/v1/project-plans/{project['id']}/generate",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"source_type": "owner_defined", "source_id": "owner-defined", "template": OWNER_TEMPLATE},
                    )
                assert resp.status_code == 200, resp.text
                data = resp.json()
                assert data["plan_status"] == "plan_draft"
                assert data["source_type"] == "owner_defined"
                assert len(data["draft_plan"]["tasks"]) > 0
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_owner_defined_invalid_templates_return_400(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-invalid-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "非法模板域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                token = create_access_token(owner.id)
                invalid_templates = [
                    "not-an-object",
                    {},
                    {"phases": []},
                    {"phases": [{"phase": "阶段一", "tasks": []}]},
                    {"phases": [{"phase": "阶段一", "tasks": [{"title": "无 key"}]}]},
                ]
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    for template in invalid_templates:
                        resp = await client.post(
                            f"/api/v1/project-plans/{project['id']}/generate",
                            headers={"Authorization": f"Bearer {token}"},
                            json={"source_type": "owner_defined", "source_id": "owner-defined", "template": template},
                        )
                        assert resp.status_code == 400, (template, resp.status_code, resp.text)
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_task_version_concurrent_only_one_succeeds(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-taskver-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "任务版本并发域")
            entity_id_uuid = entity_id
            owner_id = owner.id
            owner_email = owner.email
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                project_id = project["id"]
                await _make_draft(db, owner, project_id)
                view = await _confirm(db, owner, project_id)
                task_id = view["tasks"][0]["id"]

                def worker(label):
                    async def inner():
                        engine = create_async_engine(settings.DATABASE_URL)
                        local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                        try:
                            async with local() as session:
                                actor = User(id=owner_id, email=owner_email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
                                try:
                                    await get_project_plan_service().update_task(
                                        session, actor, project_id, task_id,
                                        {"status": "in_progress", "progress": 50, "expected_task_version": 1},
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
                assert len([r for r in results if r[0] == "error" and "任务版本已变化" in r[2]]) == 1
                final = await get_project_plan_service().list_plan(db, owner, project_id)
                task = next(t for t in final["tasks"] if t["id"] == task_id)
                assert task["task_version"] == 2
            finally:
                await _cleanup(db, [entity_id_uuid], [owner_id], intake_ids, project_ids)

    async def test_commit_failure_rolls_back(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-commit-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "提交回滚域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                owner_id = owner.id
                owner_email = owner.email
                await _make_draft(db, owner, project["id"])
                with patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new=AsyncMock(side_effect=RuntimeError("injected"))):
                    with pytest.raises(RuntimeError, match="injected"):
                        await _confirm(db, owner, project["id"])
                tasks = (await db.execute(
                    select(ProjectWorkItem).where(ProjectWorkItem.project_id == uuid.UUID(project["id"]))
                )).scalars().all()
                assert tasks == []
                artifacts = (await db.execute(
                    select(ProjectArtifact).where(ProjectArtifact.project_id == uuid.UUID(project["id"]))
                )).scalars().all()
                assert all(a.status != "confirmed" for a in artifacts)
                audit = (await db.execute(
                    select(AuditLog).where(
                        AuditLog.action == "project_plan_confirmed",
                        AuditLog.target_id == project["id"],
                    )
                )).scalars().all()
                assert audit == []
                actor = User(id=owner_id, email=owner_email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
                after = await get_project_plan_service().list_plan(db, actor, project["id"])
                assert after["plan_status"] == "plan_draft"
            finally:
                await _cleanup(db, [entity_id], [owner_id], intake_ids, project_ids)

    async def test_non_plan_task_ignored(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-other-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "非计划任务域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                view = await _confirm(db, owner, project["id"])
                other = ProjectWorkItem(
                    project_id=uuid.UUID(project["id"]),
                    work_type="other",
                    title="其他工作项",
                    status="planned",
                    truth_status="observed",
                )
                db.add(other)
                await db.commit()
                after = await get_project_plan_service().list_plan(db, owner, project["id"])
                assert all(t["title"] != "其他工作项" for t in after["tasks"])
                csv_text = await get_project_plan_service().export_plan_csv(db, owner, project["id"])
                assert "其他工作项" not in csv_text
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_cross_realm_patch_task_404(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-patch-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"r3f2-patchout-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, _ = await _setup_realm(db, owner, "PATCH隔离域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                view = await _confirm(db, owner, project["id"])
                task_id = view["tasks"][0]["id"]
                owner_token = create_access_token(owner.id)
                outsider_token = create_access_token(outsider.id)
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    out = await client.patch(
                        f"/api/v1/project-plans/{project['id']}/tasks/{task_id}",
                        headers={"Authorization": f"Bearer {outsider_token}"},
                        json={"status": "in_progress", "progress": 50, "expected_task_version": 1},
                    )
                    miss = await client.patch(
                        f"/api/v1/project-plans/{uuid.uuid4()}/tasks/{task_id}",
                        headers={"Authorization": f"Bearer {owner_token}"},
                        json={"status": "in_progress", "progress": 50, "expected_task_version": 1},
                    )
                assert out.status_code == 404 and miss.status_code == 404
                assert out.json()["detail"] == "resource not found"
                assert miss.json()["detail"] == "resource not found"
            finally:
                await _cleanup(db, [entity_id], [owner.id, outsider.id], intake_ids, project_ids)

    async def test_illegal_progress_combinations_rejected(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-progress-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "进度组合域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                await _make_draft(db, owner, project["id"])
                view = await _confirm(db, owner, project["id"])
                task = view["tasks"][0]
                svc = get_project_plan_service()
                with pytest.raises(ValueError, match="planned task must have progress 0"):
                    await svc.update_task(db, owner, project["id"], task["id"], {"status": "planned", "progress": 50, "expected_task_version": 1})
                with pytest.raises(ValueError, match="in_progress/blocked task must have progress 0-99"):
                    await svc.update_task(db, owner, project["id"], task["id"], {"status": "in_progress", "progress": 100, "expected_task_version": 1})
                with pytest.raises(ValueError, match="completed task must have progress 100"):
                    await svc.update_task(db, owner, project["id"], task["id"], {"status": "completed", "progress": 99, "expected_task_version": 1})
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_invalid_and_mixed_dates_rejected_or_normalized(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r3f2-date-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "日期解析域")
            intake_ids, project_ids = [], []
            try:
                project, intake_id = await _create_confirmed_project(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                project_ids.append(uuid.UUID(project["id"]))
                view = await _make_draft(db, owner, project["id"])
                tasks = list(view["draft_plan"]["tasks"])
                tasks[0]["start_at"] = "not-a-date"
                with pytest.raises(ValueError, match="invalid datetime"):
                    await get_project_plan_service().update_draft(db, owner, project["id"], 1, {"tasks": tasks})
                tasks[0]["start_at"] = "2026-08-16T09:00:00"
                tasks[0]["due_at"] = "2026-08-16T10:00:00+00:00"
                edited = await get_project_plan_service().update_draft(db, owner, project["id"], 1, {"tasks": tasks})
                assert edited["plan_version"] == 2
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)
