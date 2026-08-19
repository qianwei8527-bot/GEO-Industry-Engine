'''V10.5 lightweight startup and execution loop tests.'''

import shutil
import sys
import uuid

sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select, delete

from app.database import _get_session_factory
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.models.company import Company
from app.models.brand import Brand
from app.models.governance import NodeMembership
from app.models.realm import RealmRegistry
from app.models.evidence import Evidence
from app.models.geo_project import GeoProject, ProjectWorkItem, ProjectArtifact, ToolExecutionRecord, ProjectOutcome
from app.models.intake import ClientIntake, IntakeAnalysis
from app.models.issue import IssueRecord, IssueEvent
from app.services.realm_service import get_realm_service
from app.services.geo_project_service import get_geo_project_service
from app.services.intake_service import get_intake_service
from app.services.execution_plan_service import get_execution_plan_service
from app.services.issue_service import get_issue_service


def make_user(db, email, role=UserRole.ENTERPRISE):
    u = User(email=email, password_hash='x', name='域主', role=role)
    db.add(u)
    return u


async def _setup_realm(db, user):
    ws = await get_realm_service().create_enterprise(db, user, {
        'name': f'V10.5 {uuid.uuid4().hex[:6]}',
        'website': f'https://{uuid.uuid4().hex[:8]}.test',
    })
    entity_id = uuid.UUID(ws['identity']['id'])
    registry = (await db.execute(
        select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
    )).scalars().first()
    return entity_id, registry.id


async def _cleanup(db, entity_ids, user_ids, intake_ids=(), issue_ids=(), project_ids=()):
    for issue_id in issue_ids:
        await db.execute(delete(IssueEvent).where(IssueEvent.issue_id == issue_id))
        await db.execute(delete(IssueRecord).where(IssueRecord.id == issue_id))
    for intake_id in intake_ids:
        intake = await db.get(ClientIntake, intake_id)
        if intake:
            await db.execute(delete(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake_id))
            await db.execute(delete(ClientIntake).where(ClientIntake.id == intake_id))
    for pid in project_ids:
        await db.execute(delete(ProjectOutcome).where(ProjectOutcome.project_id == pid))
        await db.execute(delete(ToolExecutionRecord).where(ToolExecutionRecord.project_id == pid))
        await db.execute(delete(ProjectArtifact).where(ProjectArtifact.project_id == pid))
        await db.execute(delete(ProjectWorkItem).where(ProjectWorkItem.project_id == pid))
        await db.execute(delete(GeoProject).where(GeoProject.id == pid))
    for eid in entity_ids:
        registry = (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == eid)
        )).scalars().first()
        if registry:
            projects = (await db.execute(select(GeoProject).where(GeoProject.realm_id == registry.id))).scalars().all()
            for p in projects:
                await db.execute(delete(ProjectOutcome).where(ProjectOutcome.project_id == p.id))
                await db.execute(delete(ToolExecutionRecord).where(ToolExecutionRecord.project_id == p.id))
                await db.execute(delete(ProjectArtifact).where(ProjectArtifact.project_id == p.id))
                await db.execute(delete(ProjectWorkItem).where(ProjectWorkItem.project_id == p.id))
            await db.execute(delete(GeoProject).where(GeoProject.realm_id == registry.id))
            intakes = (await db.execute(select(ClientIntake).where(ClientIntake.realm_id == registry.id))).scalars().all()
            for intake in intakes:
                await db.execute(delete(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake.id))
                await db.execute(delete(ClientIntake).where(ClientIntake.id == intake.id))
            issues = (await db.execute(select(IssueRecord).where(IssueRecord.realm_id == registry.id))).scalars().all()
            for issue in issues:
                await db.execute(delete(IssueEvent).where(IssueEvent.issue_id == issue.id))
                await db.execute(delete(IssueRecord).where(IssueRecord.id == issue.id))
        await db.execute(delete(Evidence).where(Evidence.entity_id == eid))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(eid)))
        await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == eid))
        await db.execute(delete(Brand).where(Brand.id == eid))
        await db.execute(delete(Company).where(Company.id == eid))
        await db.execute(delete(Entity).where(Entity.id == eid))
    for uid in user_ids:
        await db.execute(delete(User).where(User.id == uid))
    await db.commit()
    for intake_id in intake_ids:
        root = get_intake_service()._upload_root('cleanup', str(intake_id))
        shutil.rmtree(root, ignore_errors=True)


SAMPLE_TEXT = (
    '试点品牌：恒域世界\n'
    '主体：深圳市恒域世界科技有限公司\n'
    '关系：附属关系\n'
    '产品：GEO运营服务\n'
    '客户：GEO行业所有客户\n'
    '地区：深圳\n'
    '问题：新公司，从零开始\n'
    '渠道：无\n'
    '转化目标：GEO相关产业的所有企业与从业者\n'
)


class TestIntakeLoop:
    async def test_upload_analyze_confirm(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f'v105i-{uuid.uuid4().hex[:8]}@x.com')
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, realm_id = await _setup_realm(db, user)
            intake_id = None
            try:
                svc = get_intake_service()
                intake = await svc.create_intake(db, user, str(realm_id), {
                    'relationship': '附属关系',
                    'pasted_text': SAMPLE_TEXT,
                    'files': [],
                })
                intake_id = uuid.UUID(intake['id'])
                assert intake['status'] == 'uploaded'
                analyzed = await svc.analyze_intake(db, user, intake['id'])
                assert analyzed['status'] == 'needs_confirmation'
                detail = await svc.get_intake(db, user, intake['id'])
                latest = detail['analyses'][0]
                fields = {f['key']: f for f in latest['analysis_json']['fields']}
                assert fields['brand_name']['value'] == '恒域世界'
                assert fields['enterprise_entity']['status'] == 'observed'
                assert fields['conversion_goals']['status'] != 'unknown'
                confirmed = await svc.confirm_intake(db, user, intake['id'], {
                    'enterprise_entity': '深圳市恒域世界科技有限公司',
                    'service_region': '深圳',
                })
                assert confirmed['status'] == 'owner_confirmed'
                intake_code = intake['intake_code']
                evidence = (await db.execute(
                    select(Evidence).where(Evidence.source_url == f'urn:geo-intake:{intake_code}')
                )).scalars().first()
                assert evidence is not None
                assert evidence.truth_status == 'observed'
                assert evidence.is_synthetic is False
            finally:
                await _cleanup(db, [entity_id], [user.id], intake_ids=[intake_id] if intake_id else [])

    async def test_file_parse_txt(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f'v105f-{uuid.uuid4().hex[:8]}@x.com')
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, realm_id = await _setup_realm(db, user)
            intake_id = None
            try:
                svc = get_intake_service()
                content = '品牌名称：恒域世界\n产品：GEO运营服务'.encode('utf-8')
                intake = await svc.create_intake(db, user, str(realm_id), {
                    'files': [{'filename': 'profile.txt', 'content_type': 'text/plain', 'content': content}],
                })
                intake_id = uuid.UUID(intake['id'])
                manifest = intake['file_manifest']
                assert manifest[0]['parse_status'] == 'parsed'
                assert '恒域世界' in manifest[0]['extracted_text']
            finally:
                await _cleanup(db, [entity_id], [user.id], intake_ids=[intake_id] if intake_id else [])


class TestExecutionPlan:
    async def test_generate_update_sync_export(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f'v105p-{uuid.uuid4().hex[:8]}@x.com')
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, realm_id = await _setup_realm(db, user)
            project_id = None
            try:
                project = await get_geo_project_service().create_project(db, user, {
                    'realm_id': str(realm_id),
                    'name': '恒域世界 GEO 首个试点',
                    'target_brand': '恒域世界',
                    'target_product': 'GEO运营服务',
                    'target_audience': 'GEO 行业企业与从业者',
                })
                project_id = uuid.UUID(project['id'])
                svc = get_execution_plan_service()
                plan = await svc.generate_plan(db, user, project['id'])
                assert len(plan['work_items']) == 8
                assert all(item['truth_status'] == 'inferred' for item in plan['work_items'])
                first = plan['work_items'][0]
                updated = await svc.update_work_item(db, user, project['id'], first['id'], {
                    'status': 'in_progress',
                    'progress': 40,
                    'acceptance_criteria': '已完成首轮确认',
                })
                assert updated['status'] == 'in_progress'
                assert updated['progress'] == 40
                synced = await svc.sync_work_item(db, user, project['id'], first['id'], {
                    'source': 'tool_execution:geo_visibility',
                    'status': 'completed',
                    'progress': 100,
                })
                assert synced['last_synced_source'] == 'tool_execution:geo_visibility'
                exported = await svc.export_plan_csv(db, user, project['id'])
                assert '阶段' in exported
                assert '恒域世界 GEO 首个试点' not in exported
            finally:
                await _cleanup(db, [entity_id], [user.id], project_ids=[project_id] if project_id else [])


class TestIssueLibrary:
    async def test_create_classify_history_template(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f'v105q-{uuid.uuid4().hex[:8]}@x.com')
            db.add(user)
            await db.commit()
            await db.refresh(user)
            entity_id, realm_id = await _setup_realm(db, user)
            issue_id = None
            try:
                svc = get_issue_service()
                issue = await svc.create_issue(db, user, str(realm_id), {
                    'original_text': '权限不足，无法提交审批',
                    'scenario': '执行计划审批',
                })
                issue_id = uuid.UUID(issue['id'])
                assert issue['category'] is None
                assert issue['status'] == 'open'
                detail = await svc.get_issue(db, user, issue['id'])
                event_types = [e['event_type'] for e in detail['events']]
                assert 'created' in event_types
                assert 'ai_classified' in event_types
                updated = await svc.update_issue(db, user, issue['id'], {
                    'status': 'triaged',
                    'final_solution': '由域主在后台补授权后重试',
                }, expected_version=1)
                assert updated['status'] == 'triaged'
                updated = await svc.update_issue(db, user, issue['id'], {
                    'status': 'in_progress',
                }, expected_version=2)
                assert updated['status'] == 'in_progress'
                assert updated['original_text'] == '权限不足，无法提交审批'
                history = [e['event_type'] for e in updated['events']]
                assert 'status_changed' in history
                assert 'solution_recorded' in history
                resolved = await svc.update_issue(db, user, issue['id'], {'status': 'resolved'}, expected_version=3)
                assert resolved['status'] == 'resolved'
                reopened = await svc.update_issue(db, user, issue['id'], {'status': 'in_progress'}, expected_version=4)
                assert reopened['status'] == 'in_progress'
                reopened_types = [e['event_type'] for e in reopened['events']]
                assert 'status_changed' in reopened_types
            finally:
                await _cleanup(db, [entity_id], [user.id], issue_ids=[issue_id] if issue_id else [])

    async def test_outsider_cannot_write(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f'v105o-{uuid.uuid4().hex[:8]}@x.com')
            outsider = make_user(db, f'v105x-{uuid.uuid4().hex[:8]}@x.com')
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, realm_id = await _setup_realm(db, owner)
            try:
                with pytest.raises(PermissionError):
                    await get_intake_service().create_intake(db, outsider, str(realm_id), {
                        'pasted_text': '客户资料',
                        'files': [],
                    })
                with pytest.raises(PermissionError):
                    await get_issue_service().create_issue(db, outsider, str(realm_id), {
                        'original_text': '外部问题',
                    })
            finally:
                await _cleanup(db, [entity_id], [owner.id, outsider.id])
