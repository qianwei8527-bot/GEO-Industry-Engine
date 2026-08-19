'''V10.5 execution plan service.

The plan is an editable AI draft. Nothing executes automatically and every
generated item is marked inferred until the owner edits and starts it.
'''

import csv
import io
import uuid
from datetime import datetime, timedelta, time, timezone
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geo_project import GeoProject, ProjectWorkItem
from app.models.realm import RealmRegistry
from app.services.geo_project_service import get_geo_project_service
from app.services.governance import get_governance_service
from app.services.realm_service import get_realm_service


class ExecutionPlanService:
    def __init__(self):
        self.realm_service = get_realm_service()
        self.gov = get_governance_service()
        self.geo_project_service = get_geo_project_service()

    async def _control(self, db: AsyncSession, user, realm_id) -> bool:
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError('realm not found')
        return await self.realm_service._control(db, user, str(registry.entity_id))

    async def _audit(self, db, user, action, target_type, target_id, reason=None, metadata=None):
        await self.gov.audit(
            db, user.id, action, target_type, target_id,
            reason=reason, actor_label=user.name, metadata=metadata,
        )

    @staticmethod
    def _build_tasks(project: GeoProject, owner_label: str) -> List[Dict]:
        today = datetime.now(timezone.utc).date()

        def iso(days: int) -> str:
            return datetime.combine(today + timedelta(days=days), time(9, 0), tzinfo=timezone.utc).isoformat()

        brand = project.target_brand or '客户品牌'
        tasks = [
            {
                'phase': '阶段一：基础认知',
                'title': '确认客户档案与品牌关系',
                'purpose': '建立可追溯的经营基线',
                'reason': '客户资料已经过域主确认，先固化品牌、主体、关系与目标。',
                'owner_label': owner_label,
                'start_at': iso(0),
                'due_at': iso(3),
                'depends_on': [],
                'acceptance_criteria': '档案字段均有来源或明确标记为待补充',
                'required_materials': ['已确认客户档案'],
                'evidence_ids': [],
                'risks': ['资料不完整时不得补造'],
                'reminder_at': iso(1),
                'execution_mode': 'owner_review',
                'status': 'planned',
                'progress': 0,
            },
            {
                'phase': '阶段一：基础认知',
                'title': '盘点行业、渠道与竞争位置',
                'purpose': '建立行业认知基线',
                'reason': '明确赛道、目标客户、渠道和竞争对象，为后续资产建设提供依据。',
                'owner_label': owner_label,
                'start_at': iso(1),
                'due_at': iso(5),
                'depends_on': ['确认客户档案与品牌关系'],
                'acceptance_criteria': '行业、渠道、竞争对象至少形成可修订清单',
                'required_materials': ['已确认客户档案', '公开行业资料'],
                'evidence_ids': [],
                'risks': ['外部资料需保留来源'],
                'reminder_at': iso(3),
                'execution_mode': 'ai_assisted_review',
                'status': 'planned',
                'progress': 0,
            },
            {
                'phase': '阶段二：资产建设',
                'title': '整理品牌事实与证据',
                'purpose': '建立可信知识资产',
                'reason': '把真实主体、产品、服务和案例整理为可引用的证据。',
                'owner_label': owner_label,
                'start_at': iso(3),
                'due_at': iso(8),
                'depends_on': ['确认客户档案与品牌关系'],
                'acceptance_criteria': '每条事实有来源、状态与待核验项',
                'required_materials': ['主体工商信息', '官方渠道', '案例记录'],
                'evidence_ids': [],
                'risks': ['observed 不得显示为 verified'],
                'reminder_at': iso(5),
                'execution_mode': 'owner_review',
                'status': 'planned',
                'progress': 0,
            },
            {
                'phase': '阶段二：资产建设',
                'title': '建立官方内容资产',
                'purpose': '为 AI 可见度实验提供可检索内容',
                'reason': '先有真实内容资产，再开展可见度检测与分发。',
                'owner_label': owner_label,
                'start_at': iso(5),
                'due_at': iso(12),
                'depends_on': ['整理品牌事实与证据'],
                'acceptance_criteria': '官方页面、产品说明、联系方式可被检索',
                'required_materials': ['品牌事实清单', '官方页面'],
                'evidence_ids': [],
                'risks': ['内容发布需要域主确认'],
                'reminder_at': iso(8),
                'execution_mode': 'content_production',
                'status': 'planned',
                'progress': 0,
            },
            {
                'phase': '阶段三：可见度实验',
                'title': '首轮 AI 可见度检测',
                'purpose': '记录实验基线',
                'reason': '用真实问题集检测品牌在 AI 回答中的出现情况，只记录不承诺排名。',
                'owner_label': owner_label,
                'start_at': iso(10),
                'due_at': iso(15),
                'depends_on': ['建立官方内容资产'],
                'acceptance_criteria': '检测结果保留问题、答案快照与时间',
                'required_materials': ['问题集', '官方内容资产'],
                'evidence_ids': [],
                'risks': ['结果受模型与时间影响，不承诺排名'],
                'reminder_at': iso(13),
                'execution_mode': 'tool_execution',
                'status': 'planned',
                'progress': 0,
            },
            {
                'phase': '阶段三：可见度实验',
                'title': '内容发布与分发',
                'purpose': '让真实内容触达目标对象',
                'reason': '在域主确认后通过真实渠道发布并记录。',
                'owner_label': owner_label,
                'start_at': iso(12),
                'due_at': iso(20),
                'depends_on': ['首轮 AI 可见度检测'],
                'acceptance_criteria': '发布记录包含渠道、时间、链接与确认人',
                'required_materials': ['内容资产', '渠道清单'],
                'evidence_ids': [],
                'risks': ['未经域主确认不得自动发布'],
                'reminder_at': iso(15),
                'execution_mode': 'manual_publish',
                'status': 'planned',
                'progress': 0,
            },
            {
                'phase': '阶段四：反馈沉淀',
                'title': '监测回填与问题收集',
                'purpose': '把执行问题沉淀进问题库',
                'reason': '收集工具、流程、权限和外部沟通问题，AI 只分类不覆盖原文。',
                'owner_label': owner_label,
                'start_at': iso(18),
                'due_at': iso(28),
                'depends_on': ['内容发布与分发'],
                'acceptance_criteria': '问题库包含原始问题、分类、状态和历史',
                'required_materials': ['问题库', '监测结果'],
                'evidence_ids': [],
                'risks': ['重复问题只建议合并，不自动合并'],
                'reminder_at': iso(22),
                'execution_mode': 'feedback_loop',
                'status': 'planned',
                'progress': 0,
            },
            {
                'phase': '阶段四：反馈沉淀',
                'title': '90 天复盘与模板沉淀',
                'purpose': '形成可复制的单赛道流程',
                'reason': '基于真实结果复盘，经域主确认后把有效方法升级为模板候选。',
                'owner_label': owner_label,
                'start_at': iso(25),
                'due_at': iso(30),
                'depends_on': ['监测回填与问题收集'],
                'acceptance_criteria': '复盘报告与模板候选均经域主确认',
                'required_materials': ['监测结果', '问题库', '项目数据'],
                'evidence_ids': [],
                'risks': ['模板只能来自真实有效方法'],
                'reminder_at': iso(28),
                'execution_mode': 'owner_review',
                'status': 'planned',
                'progress': 0,
            },
        ]
        return tasks

    async def list_plan(self, db, user, project_id) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        items = (await db.execute(
            select(ProjectWorkItem)
            .where(ProjectWorkItem.project_id == project.id)
            .order_by(ProjectWorkItem.start_at, ProjectWorkItem.created_at)
        )).scalars().all()
        now = datetime.now(timezone.utc)
        work_items = []
        reminders = []
        for item in items:
            entry = self._work_item_dict(item)
            item_reminders = self._compute_reminders(item, now)
            entry['reminders'] = item_reminders
            reminders.extend(item_reminders)
            work_items.append(entry)
        return {
            'project': self.geo_project_service._project_dict(project),
            'work_items': work_items,
            'reminders': reminders,
            'generated_at': now.isoformat(),
        }

    async def generate_plan(
        self,
        db,
        user,
        project_id,
        replace_existing: bool = False,
        simulation: bool = False,
    ) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        existing = (await db.execute(
            select(ProjectWorkItem).where(ProjectWorkItem.project_id == project.id)
        )).scalars().all()
        if existing:
            ai_draft = all(
                item.status == 'planned' and (item.metadata_json or {}).get('source') == 'ai_draft'
                for item in existing
            )
            if not replace_existing or not ai_draft:
                plan = await self.list_plan(db, user, project_id)
                plan['message'] = '已有计划，未覆盖；如需重新生成请选择“重新生成草稿”。'
                return plan
            for item in existing:
                await db.delete(item)
            await db.flush()
        tasks = self._build_tasks(project, user.name)
        for task in tasks:
            item = ProjectWorkItem(
                project_id=project.id,
                work_type='plan_task',
                title=task['title'],
                description=task.get('acceptance_criteria'),
                status='planned',
                phase=task['phase'],
                purpose=task.get('purpose'),
                reason=task.get('reason'),
                owner_id=user.id,
                start_at=self._parse_dt(task.get('start_at')),
                due_at=self._parse_dt(task.get('due_at')),
                depends_on=task.get('depends_on') or [],
                acceptance_criteria=task.get('acceptance_criteria'),
                required_materials=task.get('required_materials') or [],
                evidence_ids=task.get('evidence_ids') or [],
                risks=task.get('risks') or [],
                reminder_at=self._parse_dt(task.get('reminder_at')),
                execution_mode=task.get('execution_mode'),
                progress=0,
                operator_id=user.id,
                truth_status='synthetic' if simulation else 'inferred',
                may_affect_real_metrics=False,
                metadata_json={
                    'source': 'ai_draft',
                    'owner_label': task.get('owner_label'),
                    'plan_version': 1,
                    'simulation': simulation,
                },
            )
            db.add(item)
        project.status = 'planning'
        await db.commit()
        await self._audit(
            db, user, 'execution_plan_generated', 'geo_project', str(project.id),
            reason='AI draft plan; owner must edit and start tasks',
        )
        plan = await self.list_plan(db, user, project_id)
        plan['message'] = '已生成可编辑的 AI 计划草稿。'
        return plan

    async def update_work_item(self, db, user, project_id, work_item_id, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        item = await self._require_work_item(db, work_item_id, project.id)
        before_status = item.status
        scalar_fields = {
            'phase', 'title', 'description', 'purpose', 'reason', 'acceptance_criteria',
            'completion_note', 'status', 'execution_mode',
        }
        list_fields = {
            'depends_on', 'required_materials', 'evidence_ids', 'risks',
        }
        for key, value in (data or {}).items():
            if key in scalar_fields and value is not None:
                setattr(item, key, str(value).strip() or None)
            elif key in list_fields and value is not None:
                setattr(item, key, list(value))
            elif key == 'progress' and value is not None:
                item.progress = max(0, min(100, int(value)))
            elif key == 'owner_id' and value:
                item.owner_id = uuid.UUID(str(value))
            elif key in ('start_at', 'due_at', 'reminder_at'):
                setattr(item, key, self._parse_dt(value))
        if item.status == 'completed':
            item.progress = 100
            item.metadata_json = {**(item.metadata_json or {}), 'completed_at': datetime.now(timezone.utc).isoformat()}
        elif before_status == 'completed' and item.status != 'completed':
            item.metadata_json = {**(item.metadata_json or {}), 'reopened_at': datetime.now(timezone.utc).isoformat()}
        item.metadata_json = {**(item.metadata_json or {}), 'last_edited_by': user.name, 'last_edited_at': datetime.now(timezone.utc).isoformat()}
        await db.commit()
        await db.refresh(item)
        await self._audit(
            db, user, 'work_item_updated', 'project_work_item', str(item.id),
            reason=f'status {before_status} -> {item.status}',
        )
        return self._work_item_dict(item)

    async def sync_work_item(self, db, user, project_id, work_item_id, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        item = await self._require_work_item(db, work_item_id, project.id)
        source = (data.get('source') or '').strip()
        if not source:
            raise ValueError('source is required for auto sync')
        if data.get('status') in ('planned', 'in_progress', 'blocked', 'waiting', 'completed'):
            item.status = data['status']
        if data.get('progress') is not None:
            item.progress = max(0, min(100, int(data['progress'])))
        item.last_synced_source = source
        item.last_synced_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(item)
        await self._audit(
            db, user, 'work_item_synced_auto', 'project_work_item', str(item.id),
            reason=source,
            metadata={'source': source, 'status': item.status, 'progress': item.progress},
        )
        return self._work_item_dict(item)

    async def export_plan_csv(self, db, user, project_id) -> str:
        plan = await self.list_plan(db, user, project_id)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            '阶段', '任务', '目的', '推荐原因', '负责人', '开始时间', '截止时间',
            '前置依赖', '验收标准', '所需资料', '关联证据', '风险', '提醒时间',
            '执行方式', '完成状态', '进度', '最后同步来源',
        ])
        for item in plan['work_items']:
            writer.writerow([
                item.get('phase') or '', item.get('title') or '', item.get('purpose') or '',
                item.get('reason') or '', item.get('owner_label') or '', item.get('start_at') or '',
                item.get('due_at') or '', ';'.join(item.get('depends_on') or []),
                item.get('acceptance_criteria') or '', ';'.join(item.get('required_materials') or []),
                ';'.join(str(e) for e in (item.get('evidence_ids') or [])),
                ';'.join(item.get('risks') or []), item.get('reminder_at') or '',
                item.get('execution_mode') or '', item.get('status') or '', item.get('progress') or 0,
                item.get('last_synced_source') or '',
            ])
        await self._audit(db, user, 'execution_plan_exported', 'geo_project', project_id, reason='CSV export')
        return buffer.getvalue()

    def _work_item_dict(self, item: ProjectWorkItem) -> Dict:
        return {
            'id': str(item.id),
            'project_id': str(item.project_id),
            'work_type': item.work_type,
            'title': item.title,
            'description': item.description,
            'status': item.status,
            'phase': item.phase,
            'purpose': item.purpose,
            'reason': item.reason,
            'owner_id': str(item.owner_id) if item.owner_id else None,
            'owner_label': (item.metadata_json or {}).get('owner_label'),
            'start_at': item.start_at.isoformat() if item.start_at else None,
            'due_at': item.due_at.isoformat() if item.due_at else None,
            'depends_on': item.depends_on or [],
            'acceptance_criteria': item.acceptance_criteria,
            'required_materials': item.required_materials or [],
            'evidence_ids': item.evidence_ids or [],
            'risks': item.risks or [],
            'reminder_at': item.reminder_at.isoformat() if item.reminder_at else None,
            'execution_mode': item.execution_mode,
            'progress': item.progress,
            'completion_note': item.completion_note,
            'last_synced_source': item.last_synced_source,
            'last_synced_at': item.last_synced_at.isoformat() if item.last_synced_at else None,
            'truth_status': item.truth_status,
            'created_at': item.created_at.isoformat() if item.created_at else None,
        }

    @staticmethod
    def _compute_reminders(item: ProjectWorkItem, now: datetime) -> List[Dict]:
        reminders = []
        if item.status in ('completed', 'archived'):
            return reminders
        if item.due_at and item.due_at < now:
            reminders.append({'type': 'overdue', 'message': '任务已逾期', 'due_at': item.due_at.isoformat()})
        elif item.due_at and item.due_at <= now + timedelta(days=3):
            reminders.append({'type': 'due_soon', 'message': '3 天内到期', 'due_at': item.due_at.isoformat()})
        if item.reminder_at and item.reminder_at <= now:
            reminders.append({'type': 'reminder_due', 'message': '提醒时间已到', 'reminder_at': item.reminder_at.isoformat()})
        if item.status == 'blocked':
            reminders.append({'type': 'blocked', 'message': '任务受阻，需要处理'})
        return reminders

    async def _require_project(self, db, project_id) -> GeoProject:
        try:
            project = await db.get(GeoProject, uuid.UUID(str(project_id)))
        except (ValueError, TypeError):
            raise ValueError('project_id must be a valid UUID')
        if not project:
            raise ValueError('project not found')
        return project

    async def _require_work_item(self, db, work_item_id, project_id) -> ProjectWorkItem:
        try:
            item = await db.get(ProjectWorkItem, uuid.UUID(str(work_item_id)))
        except (ValueError, TypeError):
            raise ValueError('work_item_id must be a valid UUID')
        if not item or str(item.project_id) != str(project_id):
            raise ValueError('work item not found in project')
        return item

    @staticmethod
    def _parse_dt(value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except ValueError:
            return None


def get_execution_plan_service() -> ExecutionPlanService:
    return ExecutionPlanService()
