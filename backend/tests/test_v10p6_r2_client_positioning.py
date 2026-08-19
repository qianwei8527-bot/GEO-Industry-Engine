"""V10.6-R2 client positioning workflow tests."""

import json
import asyncio
import concurrent.futures
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import create_access_token
from app.database import _get_session_factory
from app.main import app
from app.models.entity import Entity
from app.models.company import Company
from app.models.evidence import Evidence
from app.models.geo_project import GeoProject
from app.models.governance import AuditLog, NodeMembership
from app.models.intake import ClientIntake, IntakeAnalysis
from app.models.realm import RealmRegistry
from app.models.reputation import Reputation
from app.models.user import User, UserRole
from app.services.geo_project_service import get_geo_project_service
from app.services.intake_service import get_intake_service
from app.services.intake_service import IntakeStateTransitionError
from app.services.positioning_service import get_positioning_service
from app.services.realm_service import get_realm_service


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
            "品牌名称：恒域测试品牌\n"
            "企业主体：测试企业有限公司\n"
            "产品：GEO测试服务\n"
            "问题：从零开始建立GEO认知\n"
        ),
        "files": [],
    })
    await svc.analyze_intake(db, user, intake["id"])
    return intake["id"]


async def _cleanup(db, entity_ids, user_ids, intake_ids=(), project_ids=()):
    for project_id in project_ids:
        await db.execute(delete(GeoProject).where(GeoProject.id == project_id))
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


class TestClientPositioning:
    async def test_full_flow_versioning_and_project_handoff(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r2-owner-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "R2定位域")
            intake_ids = []
            project_ids = []
            try:
                svc = get_intake_service()
                intake_id = await _create_analyzed_intake(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))

                workbench = await svc.get_workbench(db, owner, intake_id)
                assert workbench["flow_status"] == "awaiting_review"
                fields = workbench["analyses"][0]["analysis_json"]["fields"]
                brand = next(f for f in fields if f["key"] == "brand_name")
                assert brand["status"] == "observed"
                assert brand["confidence"] > 0

                await svc.start_review(db, owner, intake_id)
                updated = await svc.update_profile(
                    db, owner, intake_id,
                    {"brand_name": "恒域测试品牌（修正）"},
                    expected_version=1,
                )
                assert updated["version"] == 2
                with pytest.raises(IntakeStateTransitionError):
                    await svc.generate_positioning(db, owner, intake_id)
                with pytest.raises(IntakeStateTransitionError):
                    await svc.confirm_positioning(db, owner, intake_id)
                with pytest.raises(ValueError, match="版本已变化"):
                    await svc.update_profile(
                        db, owner, intake_id,
                        {"brand_name": "旧版本写入"},
                        expected_version=1,
                    )

                confirmed = await svc.confirm_profile(db, owner, intake_id, expected_version=2)
                assert confirmed["flow_status"] == "profile_confirmed"
                assert confirmed["status"] == "owner_confirmed"
                with pytest.raises(IntakeStateTransitionError):
                    await svc.start_review(db, owner, intake_id)
                with pytest.raises(IntakeStateTransitionError):
                    await svc.update_profile(db, owner, intake_id, {"brand_name": "跳步修改"})
                evidence = (await db.execute(
                    select(Evidence).where(Evidence.entity_id == entity_id)
                )).scalars().first()
                assert evidence is not None
                assert evidence.truth_status == "observed"
                assert evidence.verified is False
                reputation_count = (await db.execute(
                    select(Reputation).where(Reputation.node_id == entity_id)
                )).scalars().all()
                assert len(reputation_count) == 0

                draft = await svc.generate_positioning(db, owner, intake_id)
                assert draft["status"] == "positioning_draft"
                positioning = draft["analysis_json"]["positioning"]
                assert positioning["industry_position"]["industry_track"] == "待补充"
                assert "前10%" not in json.dumps(positioning, ensure_ascii=False)
                assert positioning["config_hash"]

                assert draft["analysis_json"]["positioning"]["positioning_hash"]

                confirmed_pos = await svc.confirm_positioning(
                    db, owner, intake_id,
                    {"priority_direction": "先补齐行业赛道"},
                    expected_version=draft["version"],
                )
                assert confirmed_pos["status"] == "positioning_confirmed"
                with pytest.raises(IntakeStateTransitionError):
                    await svc.confirm_positioning(db, owner, intake_id)

                project_service = get_geo_project_service()
                with pytest.raises(ValueError, match="显式确认"):
                    await project_service.create_project_from_positioning(
                        db, owner, intake_id, confirmed=False
                    )
                project = await project_service.create_project_from_positioning(
                    db, owner, intake_id, confirmed=True,
                    expected_position_version=confirmed_pos["metadata_json"]["positioning_version"],
                )
                project_ids.append(uuid.UUID(project["id"]))
                assert project["metadata_json"]["intake_id"] == intake_id
                assert project["metadata_json"]["positioning_status"] == "confirmed"
                expected_project_code = (
                    f"GEO-P-{uuid.uuid5(uuid.NAMESPACE_URL, f'positioning:{uuid.UUID(intake_id)}').hex.upper()}"
                )
                assert project["project_code"] == expected_project_code
                assert len(project["project_code"]) == len("GEO-P-") + 32
                workbench_before = await svc.get_workbench(db, owner, intake_id)
                assert project["realm_id"] == workbench_before["realm_id"]

                duplicate = await project_service.create_project_from_positioning(
                    db, owner, intake_id, confirmed=True
                )
                assert duplicate["id"] == project["id"]

                workbench = await svc.get_workbench(db, owner, intake_id)
                assert workbench["flow_status"] == "project_created"
                assert workbench["project_id"] == project["id"]
                with pytest.raises(IntakeStateTransitionError):
                    await svc.start_review(db, owner, intake_id)
                with pytest.raises(IntakeStateTransitionError):
                    await svc.confirm_profile(db, owner, intake_id)
                with pytest.raises(IntakeStateTransitionError):
                    await svc.confirm_positioning(db, owner, intake_id)

                audit = (await db.execute(
                    select(AuditLog).where(
                        AuditLog.action == "positioning_confirmed",
                        AuditLog.target_id == intake_id,
                    )
                )).scalars().first()
                assert audit is not None
                assert "恒域测试品牌" not in json.dumps(audit.metadata_json, ensure_ascii=False)
                assert "从零开始建立GEO认知" not in json.dumps(audit.metadata_json, ensure_ascii=False)
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, project_ids)

    async def test_two_realms_are_isolated(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner_a = make_user(db, f"r2-a-{uuid.uuid4().hex[:8]}@x.com")
            owner_b = make_user(db, f"r2-b-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"r2-out-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner_a, owner_b, outsider])
            await db.commit()
            await db.refresh(owner_a)
            await db.refresh(owner_b)
            await db.refresh(outsider)
            entity_a, _ = await _setup_realm(db, owner_a, "Realm A")
            entity_b, _ = await _setup_realm(db, owner_b, "Realm B")
            intake_ids = []
            try:
                intake_a = await _create_analyzed_intake(db, owner_a, entity_a, "品牌A：甲企业")
                intake_ids.append(uuid.UUID(intake_a))
                intake_b = await _create_analyzed_intake(db, owner_b, entity_b, "品牌B：乙企业")
                intake_ids.append(uuid.UUID(intake_b))

                with pytest.raises(PermissionError):
                    await get_intake_service().get_workbench(db, owner_a, intake_b)
                with pytest.raises(PermissionError):
                    await get_intake_service().get_workbench(db, outsider, intake_a)

                mine = await get_intake_service().list_intakes(db, owner_a, str(entity_a))
                assert len(mine) == 1
                assert mine[0]["id"] == intake_a
            finally:
                await _cleanup(
                    db,
                    [entity_a, entity_b],
                    [owner_a.id, owner_b.id, outsider.id],
                    intake_ids,
                )

    async def test_local_positioning_is_deterministic_without_external_ai(self):
        fields = [
            {"key": "brand_name", "label": "品牌名称", "value": "本地品牌", "status": "observed"},
            {"key": "product_service", "label": "产品", "value": "本地服务", "status": "observed"},
            {"key": "client_problem", "label": "问题", "value": "从零开始建立GEO认知", "status": "observed"},
            {"key": "industry_track", "label": "行业赛道", "value": "待补充", "status": "unknown"},
        ]
        svc = get_positioning_service()
        first = svc.generate(fields)
        second = svc.generate(fields)
        assert first["config_hash"] == second["config_hash"]
        assert first["positioning_hash"] == second["positioning_hash"]
        assert first["industry_position"]["industry_track"] == "待补充"
        assert "前10%" not in str(first)

    async def test_cross_realm_api_does_not_leak_existence(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r2-api-owner-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"r2-api-out-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, _ = await _setup_realm(db, owner, "API隔离域")
            intake_ids = []
            try:
                intake_id = await _create_analyzed_intake(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                owner_token = create_access_token(owner.id)
                outsider_token = create_access_token(outsider.id)
                endpoints = [
                    ("GET", f"/api/v1/intakes/{intake_id}/workbench"),
                    ("POST", f"/api/v1/intakes/{intake_id}/review/start"),
                    ("POST", f"/api/v1/intakes/{intake_id}/profile"),
                    ("POST", f"/api/v1/intakes/{intake_id}/profile/confirm"),
                    ("POST", f"/api/v1/intakes/{intake_id}/supplement"),
                    ("POST", f"/api/v1/intakes/{intake_id}/positioning/generate"),
                    ("POST", f"/api/v1/intakes/{intake_id}/positioning/confirm"),
                    ("POST", f"/api/v1/intakes/{intake_id}/project"),
                ]
                missing_id = str(uuid.uuid4())
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    for method, path in endpoints:
                        outsider_response = await client.request(
                            method,
                            path,
                            headers={"Authorization": f"Bearer {outsider_token}"},
                            json={} if method == "POST" else None,
                        )
                        missing_response = await client.request(
                            method,
                            path.replace(intake_id, missing_id),
                            headers={"Authorization": f"Bearer {owner_token}"},
                            json={} if method == "POST" else None,
                        )
                        assert outsider_response.status_code == 404, (
                            f"{method} {path}: {outsider_response.status_code} {outsider_response.text}"
                        )
                        assert missing_response.status_code == 404, (
                            f"{method} missing {path}: {missing_response.status_code} {missing_response.text}"
                        )
                        assert outsider_response.json()["detail"] == "resource not found"
                        assert missing_response.json()["detail"] == "resource not found"
            finally:
                await _cleanup(
                    db,
                    [entity_id],
                    [owner.id, outsider.id],
                    intake_ids,
                )

    async def test_concurrent_project_trigger_is_idempotent(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r2-concurrent-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "并发幂等域")
            entity_id_uuid = entity_id
            owner_id = owner.id
            svc = get_intake_service()
            intake_id = await _create_analyzed_intake(db, owner, entity_id)
            intake_id_uuid = uuid.UUID(intake_id)
            await svc.start_review(db, owner, intake_id)
            await svc.update_profile(db, owner, intake_id, {"target_customer": "AI行业客户"})
            await svc.confirm_profile(db, owner, intake_id)
            await svc.generate_positioning(db, owner, intake_id)
            await svc.confirm_positioning(db, owner, intake_id)
            await db.commit()

        actor = User(id=owner_id, email="concurrent@x.com", password_hash="x", name="域主", role=UserRole.ENTERPRISE)
        project_ids = []
        async with factory() as db1, factory() as db2:
            async def run(session):
                return await get_geo_project_service().create_project_from_positioning(
                    session, actor, intake_id, confirmed=True
                )

            results = await asyncio.wait_for(
                asyncio.gather(run(db1), run(db2), return_exceptions=True),
                timeout=30,
            )
            projects = [r for r in results if not isinstance(r, Exception)]
            assert len(projects) == 2
            assert projects[0]["id"] == projects[1]["id"]
            project_ids.append(uuid.UUID(projects[0]["id"]))
            await _cleanup(db1, [entity_id_uuid], [owner_id], [intake_id_uuid], project_ids)

    async def test_concurrent_expected_version_update_only_one_succeeds(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r2-version-lock-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "并发版本锁域")
            entity_id_uuid = entity_id
            owner_id = owner.id
            owner_email = owner.email
            intake_id = await _create_analyzed_intake(db, owner, entity_id)
            intake_id_uuid = uuid.UUID(intake_id)
            await get_intake_service().start_review(db, owner, intake_id)
            await db.commit()

        def run_update(label):
            async def inner():
                engine = create_async_engine(settings.DATABASE_URL)
                local_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                try:
                    async with local_factory() as session:
                        actor = User(
                            id=owner_id,
                            email=owner_email,
                            password_hash="x",
                            name="域主",
                            role=UserRole.ENTERPRISE,
                        )
                        try:
                            await get_intake_service().update_profile(
                                session, actor, intake_id,
                                {"brand_name": label},
                                expected_version=1,
                            )
                            return ("ok", label)
                        except Exception as exc:
                            return ("error", type(exc).__name__, str(exc))
                finally:
                    await engine.dispose()
            return asyncio.run(inner())

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            future_a = pool.submit(run_update, "并发版本A")
            future_b = pool.submit(run_update, "并发版本B")
            results = [future.result(timeout=30) for future in (future_a, future_b)]

        ok = [r for r in results if r[0] == "ok"]
        errors = [r for r in results if r[0] == "error"]
        assert len(ok) == 1, results
        assert len(errors) == 1
        assert "版本已变化" in errors[0][2]

        async with factory() as db:
            rows = (await db.execute(
                select(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake_id_uuid)
            )).scalars().all()
            versions = [row.version for row in rows]
            assert len(versions) == len(set(versions))
            await _cleanup(db, [entity_id_uuid], [owner_id], [intake_id_uuid])

    async def test_project_retry_rejects_wrong_intake_and_rolls_back(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"r2-project-mismatch-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner, "错误Intake回退域")
            entity_id_uuid = entity_id
            owner_id = owner.id
            intake_ids = []
            project_ids = []
            try:
                svc = get_intake_service()
                intake_id = await _create_analyzed_intake(db, owner, entity_id)
                intake_ids.append(uuid.UUID(intake_id))
                await svc.start_review(db, owner, intake_id)
                await svc.update_profile(db, owner, intake_id, {"target_customer": "行业客户"})
                await svc.confirm_profile(db, owner, intake_id)
                draft = await svc.generate_positioning(db, owner, intake_id)
                await svc.confirm_positioning(db, owner, intake_id, expected_version=draft["version"])

                project_code = (
                    f"GEO-P-{uuid.uuid5(uuid.NAMESPACE_URL, f'positioning:{uuid.UUID(intake_id)}').hex.upper()}"
                )
                registry = (await db.execute(
                    select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
                )).scalars().first()
                foreign = GeoProject(
                    project_code=project_code,
                    realm_id=registry.id,
                    realm_entity_id=registry.entity_id,
                    name="错误Intake项目",
                    status="draft",
                    truth_status="observed",
                    metadata_json={"intake_id": str(uuid.uuid4()), "source": "positioning_handoff"},
                )
                db.add(foreign)
                await db.commit()
                await db.refresh(foreign)
                project_ids.append(foreign.id)

                actor = User(
                    id=owner.id,
                    email=owner.email,
                    password_hash="x",
                    name="域主",
                    role=UserRole.ENTERPRISE,
                )
                with pytest.raises(ValueError, match="does not match realm or intake"):
                    await get_geo_project_service().create_project_from_positioning(
                        db, actor, intake_id, confirmed=True
                    )

                workbench = await svc.get_workbench(db, actor, intake_id)
                assert workbench["flow_status"] == "positioning_confirmed"
                assert workbench.get("project_id") is None
                project_count = (await db.execute(
                    select(GeoProject).where(GeoProject.metadata_json["intake_id"].as_string() == intake_id)
                )).scalars().all()
                assert len(project_count) == 0
            finally:
                await _cleanup(db, [entity_id_uuid], [owner_id], intake_ids, project_ids)
