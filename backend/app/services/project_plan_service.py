"""V10.6-R3 project plan service.

Reuses GeoProject metadata, ProjectArtifact snapshots and ProjectWorkItem
rows. No new parallel Project/Task model is introduced.
"""

import csv
import hashlib
import io
import json
import os
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Dict, List, Optional

import yaml
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geo_project import GeoProject, ProjectArtifact, ProjectWorkItem
from app.services.governance import get_governance_service
from app.services.realm_service import get_realm_service


class PlanStateError(Exception):
    pass


def _load_plan_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "config", "universe", "project_plan.yaml",
    )
    if os.path.exists(p):
        raw = open(p, encoding="utf-8").read()
        data = yaml.safe_load(raw) or {}
        data["config_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return data
    return {"version": "1.0.0", "config_hash": "missing", "workflow_sources": [], "template": {}}


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            raise ValueError("invalid datetime")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class ProjectPlanService:
    def __init__(self):
        self.config = _load_plan_config()
        self.realm_service = get_realm_service()
        self.gov = get_governance_service()

    async def _control(self, db, user, realm_id) -> bool:
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError("realm not found")
        return await self.realm_service._control(db, user, str(registry.entity_id))

    async def _audit(self, db, user, action, target_type, target_id, reason=None, metadata=None, commit: bool = True):
        await self.gov.audit(
            db, user.id, action, target_type, target_id,
            reason=reason, actor_label=user.name, metadata=metadata, commit=commit,
        )

    async def _require_project(self, db, project_id: str, lock: bool = False) -> GeoProject:
        try:
            project_uuid = uuid.UUID(str(project_id))
        except (ValueError, TypeError):
            raise ValueError("project_id must be a valid UUID")
        if lock:
            rows = (await db.execute(
                select(GeoProject).where(GeoProject.id == project_uuid).with_for_update()
            )).scalars().all()
            project = rows[0] if rows else None
        else:
            project = await db.get(GeoProject, project_uuid)
        if not project:
            raise ValueError("project not found")
        return project

    async def _confirm_permission(self, db, user, project) -> bool:
        if self.gov.is_system_admin(user):
            return True
        roles = await self.gov.get_node_roles(db, user.id, str(project.realm_entity_id or project.realm_id))
        allowed = set(self.config.get("confirm_roles", ["node_owner"]))
        return bool(set(roles) & allowed)

    async def _is_realm_member(self, db, user_id, project) -> bool:
        roles = await self.gov.get_node_roles(db, user_id, str(project.realm_entity_id or project.realm_id))
        return bool(roles)

    async def _require_task(self, db, project_id, task_id, lock: bool = False) -> ProjectWorkItem:
        try:
            task_uuid = uuid.UUID(str(task_id))
            project_uuid = uuid.UUID(str(project_id))
        except (ValueError, TypeError):
            raise ValueError("task_id or project_id must be a valid UUID")
        stmt = select(ProjectWorkItem).where(
            ProjectWorkItem.id == task_uuid,
            ProjectWorkItem.project_id == project_uuid,
            ProjectWorkItem.work_type == "plan_task",
        )
        if lock:
            stmt = stmt.with_for_update()
        rows = (await db.execute(stmt)).scalars().all()
        if not rows:
            raise ValueError("task not found")
        return rows[0]

    @staticmethod
    def _canonical(data) -> str:
        return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    def _hash_plan(self, payload: Dict) -> str:
        data = dict(payload)
        for key in (
            "project_id", "realm_id", "plan_version", "plan_hash",
            "created_by", "created_at", "updated_by", "updated_at",
            "confirmed_by", "confirmed_at",
            "owner_id", "source_owner_id", "submitted_by",
        ):
            data.pop(key, None)
        return hashlib.sha256(self._canonical(data).encode("utf-8")).hexdigest()

    def _resolve_source(self, source_type: str, source_id: Optional[str], template: Optional[Dict]) -> Dict:
        source_type = (source_type or "").strip()
        allowed_types = {"platform_seed", "owner_defined", "owner_seeded", "realm_template", "imported"}
        if source_type not in allowed_types:
            raise ValueError("invalid workflow source_type")
        if source_type == "owner_defined":
            if not isinstance(template, dict):
                raise ValueError("owner_defined template must be an object")
            phases = template.get("phases")
            if not isinstance(phases, list) or not phases:
                raise ValueError("owner_defined template must contain non-empty phases array")
            for phase in phases:
                if not isinstance(phase, dict) or not isinstance(phase.get("tasks"), list) or not phase.get("tasks"):
                    raise ValueError("owner_defined template contains invalid phase structure")
                for task in phase["tasks"]:
                    if not isinstance(task, dict) or not str(task.get("task_key") or "").strip() or not str(task.get("title") or "").strip():
                        raise ValueError("owner_defined template contains invalid task structure")
            if source_id and source_id != "owner-defined":
                raise ValueError("source_type/source_id mismatch")
            return {
                "source_type": "owner_defined",
                "source_id": source_id or "owner-defined",
                "source_version": "owner",
                "source_hash": hashlib.sha256(self._canonical(template).encode("utf-8")).hexdigest()[:16],
                "owner_confirmed": True,
                "truth_scope": "inferred",
                "template": template,
                "provenance": "owner_defined_submission",
                "owner_id": None,
            }
        source_id = source_id or "platform-seed-blank"
        for source in self.config.get("workflow_sources", []):
            if source.get("source_id") == source_id:
                if source.get("source_type") != source_type:
                    raise ValueError("source_type/source_id mismatch")
                return {
                    "source_type": source.get("source_type", "platform_seed"),
                    "source_id": source.get("source_id"),
                    "source_version": source.get("source_version", self.config.get("version", "1.0.0")),
                    "source_hash": source.get("source_hash") or self.config.get("config_hash", ""),
                    "owner_confirmed": source.get("owner_confirmed", False),
                    "truth_scope": source.get("truth_scope", "inferred"),
                    "template": self.config.get("template") or {},
                    "provenance": source.get("provenance") or source.get("source_type"),
                    "owner_id": source.get("owner_id"),
                }
        raise ValueError("workflow source not found")

    def _build_plan(self, project: GeoProject, source: Dict, submitted_by: str = None) -> Dict:
        meta = project.metadata_json or {}
        positioning = (meta.get("positioning_summary") or {})
        template = source.get("template") or {}
        phases = []
        tasks = []
        if source.get("source_type") == "platform_seed":
            phases = [{"phase": "未命名阶段", "title": "未命名阶段"}]
        else:
            for phase in template.get("phases", []):
                phase_name = phase.get("phase") or "未命名阶段"
                phases.append({"phase": phase_name, "title": phase_name})
                for task in phase.get("tasks", []):
                    tasks.append({
                        "task_key": task.get("task_key") or f"task-{uuid.uuid4().hex[:8]}",
                        "phase": phase_name,
                        "title": task.get("title") or "未命名任务",
                        "purpose": task.get("purpose") or "",
                        "description": task.get("description") or "",
                        "expected_output": task.get("expected_output") or "",
                        "acceptance_criteria": task.get("acceptance_criteria") or "",
                        "required_materials": task.get("required_materials") or [],
                        "owner_id": None,
                        "start_at": None,
                        "due_at": None,
                        "reminder_at": None,
                        "depends_on": task.get("depends_on") or [],
                        "risks": task.get("risks") or [],
                        "execution_mode": task.get("execution_mode") or "owner_review",
                        "progress": 0,
                        "status": "planned",
                        "truth_scope": "inferred",
                    })
        unknown_items = []
        if not project.target_brand:
            unknown_items.append("target_brand")
        if not project.target_audience:
            unknown_items.append("target_audience")
        if not project.objective:
            unknown_items.append("objective")
        if not positioning.get("priority_direction"):
            unknown_items.append("priority_direction")
        unknown_items.extend(["task_owners_unassigned", "task_dates_unassigned"])
        return {
            "project_id": str(project.id),
            "realm_id": str(project.realm_id),
            "plan_version": None,
            "plan_status": "plan_draft",
            "source_type": source.get("source_type"),
            "source_id": source.get("source_id"),
            "source_version": source.get("source_version"),
            "source_hash": source.get("source_hash"),
            "owner_id": None,
            "source_owner_id": source.get("owner_id"),
            "submitted_by": submitted_by,
            "owner_confirmed": source.get("owner_confirmed", False),
            "provenance": source.get("provenance"),
            "positioning_version": meta.get("positioning_version"),
            "positioning_hash": meta.get("positioning_hash"),
            "profile_version": meta.get("profile_version"),
            "config_hash": self.config.get("config_hash"),
            "plan_hash": None,
            "created_by": None,
            "created_at": None,
            "confirmed_by": None,
            "confirmed_at": None,
            "truth_scope": "inferred",
            "unknown_items": unknown_items,
            "phases": phases,
            "tasks": tasks,
        }

    def _validate_tasks(self, tasks: List[Dict]) -> None:
        keys = []
        for task in tasks:
            key = (task.get("task_key") or "").strip()
            if not key:
                raise ValueError("task_key is required")
            keys.append(key)
            progress = task.get("progress", 0)
            if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
                raise ValueError("progress must be between 0 and 100")
            status = task.get("status", "planned")
            if status not in ("planned", "in_progress", "blocked", "completed"):
                raise ValueError("invalid task status")
            if status == "planned" and progress != 0:
                raise ValueError("planned task must have progress 0")
            if status in ("in_progress", "blocked") and progress >= 100:
                raise ValueError("in_progress/blocked task must have progress 0-99")
            if status == "completed" and progress != 100:
                raise ValueError("completed task must have progress 100")
            start = _parse_dt(task.get("start_at"))
            due = _parse_dt(task.get("due_at"))
            reminder = _parse_dt(task.get("reminder_at"))
            if start and due and due < start:
                raise ValueError("due_at must not be earlier than start_at")
            if reminder and start and reminder < start:
                raise ValueError("reminder_at must not be earlier than start_at")
        if len(keys) != len(set(keys)):
            raise ValueError("task_key must be unique")
        for task in tasks:
            key = task.get("task_key")
            start = _parse_dt(task.get("start_at"))
            for dep in task.get("depends_on") or []:
                if dep not in keys:
                    raise ValueError(f"dependency {dep} does not belong to the plan")
                dep_task = next((t for t in tasks if t.get("task_key") == dep), None)
                dep_due = _parse_dt(dep_task.get("due_at")) if dep_task else None
                if start and dep_due and start < dep_due:
                    raise ValueError("dependent task must not start before prerequisite due_at")
        # cycle check
        visiting = set()
        visited = set()

        def visit(key):
            if key in visiting:
                raise ValueError("task dependency cycle detected")
            if key in visited:
                return
            visiting.add(key)
            task = next((t for t in tasks if t.get("task_key") == key), None)
            for dep in (task or {}).get("depends_on") or []:
                visit(dep)
            visiting.remove(key)
            visited.add(key)

        for key in keys:
            visit(key)

    async def list_workflow_sources(self, db, user) -> Dict:
        sources = []
        for source in self.config.get("workflow_sources", []):
            sources.append({
                "source_id": source.get("source_id"),
                "source_type": source.get("source_type"),
                "name": source.get("name"),
                "description": source.get("description"),
                "owner_confirmed": source.get("owner_confirmed", False),
                "truth_scope": source.get("truth_scope", "inferred"),
                "source_version": source.get("source_version"),
                "provenance": source.get("provenance"),
                "owner_id": source.get("owner_id"),
            })
        sources.append({
            "source_id": "owner-defined",
            "source_type": "owner_defined",
            "name": "域主自定义模板",
            "description": "域主直接创建的工作流来源",
            "owner_confirmed": True,
            "truth_scope": "inferred",
            "source_version": "owner",
            "provenance": "owner_defined_submission",
            "owner_id": None,
        })
        return {"workflow_sources": sources, "config_hash": self.config.get("config_hash")}

    async def generate_plan(
        self, db, user, project_id: str, source_type: str, source_id: str = None, template: Dict = None,
    ) -> Dict:
        project = await self._require_project(db, project_id, lock=True)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm member permission required")
        meta = project.metadata_json or {}
        current = meta.get("plan_status") or "project_created"
        if current not in ("project_created",):
            raise PlanStateError(f"invalid_state_transition: {current} -> plan_draft")
        source = self._resolve_source(source_type, source_id, template)
        payload = self._build_plan(project, source, submitted_by=str(user.id))
        plan_version = (meta.get("plan_version") or 0) + 1
        plan_hash = self._hash_plan(payload)
        now = datetime.now(timezone.utc)
        payload.update({
            "plan_version": plan_version,
            "plan_hash": plan_hash,
            "created_by": str(user.id),
            "created_at": now.isoformat(),
        })
        artifact = ProjectArtifact(
            project_id=project.id,
            artifact_type="project_plan",
            title=f"计划草稿 v{plan_version}",
            content_json=payload,
            status="draft",
            operator_id=user.id,
            truth_status="observed",
            may_affect_real_metrics=False,
            metadata_json={
                "plan_version": plan_version,
                "plan_hash": plan_hash,
                "source_type": source.get("source_type"),
                "source_id": source.get("source_id"),
                "source_version": source.get("source_version"),
                "source_hash": source.get("source_hash"),
                "plan_status": "plan_draft",
            },
        )
        db.add(artifact)
        project.metadata_json = {
            **(meta or {}),
            "plan_status": "plan_draft",
            "plan_version": plan_version,
            "plan_hash": plan_hash,
            "source_type": source.get("source_type"),
            "source_id": source.get("source_id"),
            "source_version": source.get("source_version"),
            "source_hash": source.get("source_hash"),
            "plan_realm_id": str(project.realm_id),
            "plan_owner_id": None,
            "plan_submitted_by": str(user.id),
            "plan_source_owner_id": source.get("owner_id"),
            "plan_owner_confirmed": source.get("owner_confirmed", False),
            "plan_provenance": source.get("provenance"),
            "positioning_version": meta.get("positioning_version"),
            "positioning_hash": meta.get("positioning_hash"),
            "profile_version": meta.get("profile_version"),
            "config_hash": self.config.get("config_hash"),
            "plan_created_by": str(user.id),
            "plan_created_at": now.isoformat(),
        }
        await self._audit(
            db, user, "project_plan_draft_generated", "geo_project", str(project.id),
            reason=f"plan draft v{plan_version}",
            metadata={"plan_version": plan_version, "plan_hash": plan_hash},
        )
        return await self.list_plan(db, user, project_id)

    async def update_draft(
        self, db, user, project_id: str, expected_version: int, plan: Dict,
    ) -> Dict:
        project = await self._require_project(db, project_id, lock=True)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm member permission required")
        meta = project.metadata_json or {}
        if meta.get("plan_status") != "plan_draft":
            raise PlanStateError(f"invalid_state_transition: {meta.get('plan_status', 'unknown')} -> plan_draft_edit")
        if expected_version is None or int(expected_version) != (meta.get("plan_version") or 0):
            raise ValueError("计划版本已变化，请刷新后重试")
        current = await self._latest_artifact(db, project.id)
        base = dict(current.content_json or {}) if current else {}
        tasks = plan.get("tasks") if plan.get("tasks") is not None else base.get("tasks", [])
        phases = plan.get("phases") if plan.get("phases") is not None else base.get("phases", [])
        self._validate_tasks(tasks)
        version = int(meta.get("plan_version") or 0) + 1
        now = datetime.now(timezone.utc)
        payload = {
            **(base or {}),
            "plan_version": version,
            "plan_status": "plan_draft",
            "phases": phases,
            "tasks": tasks,
            "updated_by": str(user.id),
            "updated_at": now.isoformat(),
        }
        plan_hash = self._hash_plan(payload)
        payload["plan_hash"] = plan_hash
        artifact = ProjectArtifact(
            project_id=project.id,
            artifact_type="project_plan",
            title=f"计划草稿 v{version}",
            content_json=payload,
            status="draft",
            operator_id=user.id,
            truth_status="observed",
            may_affect_real_metrics=False,
            metadata_json={"plan_version": version, "plan_hash": plan_hash, "plan_status": "plan_draft"},
        )
        db.add(artifact)
        project.metadata_json = {
            **(meta or {}),
            "plan_version": version,
            "plan_hash": plan_hash,
        }
        await self._audit(
            db, user, "project_plan_draft_updated", "geo_project", str(project.id),
            reason=f"plan draft v{version}",
            metadata={"plan_version": version, "plan_hash": plan_hash},
        )
        return await self.list_plan(db, user, project_id)

    async def confirm_plan(self, db, user, project_id: str, confirmed: bool, expected_version: int) -> Dict:
        project = await self._require_project(db, project_id, lock=True)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm member permission required")
        if not confirmed:
            raise ValueError("显式确认后才能生成正式任务")
        if not await self._confirm_permission(db, user, project):
            raise PermissionError("plan confirm requires realm owner")
        meta = project.metadata_json or {}
        current_status = meta.get("plan_status") or "project_created"
        current_version = meta.get("plan_version") or 0
        if current_status in ("plan_confirmed", "plan_active", "plan_completed"):
            if expected_version is not None and int(expected_version) != current_version:
                raise ValueError("计划版本已变化，请刷新后重试")
            existing_tasks = (await db.execute(
                select(ProjectWorkItem).where(
                    ProjectWorkItem.project_id == project.id,
                    ProjectWorkItem.work_type == "plan_task",
                )
            )).scalars().all()
            if existing_tasks:
                return await self.list_plan(db, user, project_id)
        if current_status != "plan_draft":
            raise PlanStateError(f"invalid_state_transition: {current_status} -> plan_confirmed")
        if expected_version is None or int(expected_version) != current_version:
            raise ValueError("计划版本已变化，请刷新后重试")
        artifact = await self._latest_artifact(db, project.id)
        if not artifact:
            raise ValueError("计划草稿不存在")
        payload = dict(artifact.content_json or {})
        tasks = payload.get("tasks", [])
        if not tasks:
            raise ValueError("不能确认零任务计划")
        self._validate_tasks(tasks)
        for task in tasks:
            if task.get("owner_id"):
                try:
                    owner_uuid = uuid.UUID(str(task["owner_id"]))
                except (ValueError, TypeError):
                    raise ValueError("任务负责人不是当前 Realm 有效成员")
                if not await self._is_realm_member(db, owner_uuid, project):
                    raise ValueError("任务负责人不是当前 Realm 有效成员")
        now = datetime.now(timezone.utc)
        version = int(current_version)
        confirmed_payload = {
            **(payload or {}),
            "plan_status": "plan_confirmed",
            "confirmed_by": str(user.id),
            "confirmed_at": now.isoformat(),
        }
        confirmed_hash = self._hash_plan(confirmed_payload)
        confirmed_payload["plan_hash"] = confirmed_hash
        snapshot = ProjectArtifact(
            project_id=project.id,
            artifact_type="project_plan",
            title=f"计划确认快照 v{version}",
            content_json=confirmed_payload,
            status="confirmed",
            operator_id=user.id,
            truth_status="observed",
            may_affect_real_metrics=False,
            metadata_json={"plan_version": version, "plan_hash": confirmed_hash, "plan_status": "plan_confirmed"},
        )
        db.add(snapshot)
        for task in tasks:
            item = ProjectWorkItem(
                project_id=project.id,
                work_type="plan_task",
                title=task.get("title") or "未命名任务",
                description=task.get("description"),
                status="planned",
                phase=task.get("phase"),
                purpose=task.get("purpose"),
                acceptance_criteria=task.get("acceptance_criteria"),
                required_materials=task.get("required_materials") or [],
                owner_id=uuid.UUID(str(task["owner_id"])) if task.get("owner_id") else None,
                start_at=_parse_dt(task.get("start_at")),
                due_at=_parse_dt(task.get("due_at")),
                reminder_at=_parse_dt(task.get("reminder_at")),
                depends_on=task.get("depends_on") or [],
                risks=task.get("risks") or [],
                execution_mode=task.get("execution_mode"),
                progress=task.get("progress", 0),
                operator_id=user.id,
                input_manifest={
                    "task_key": task.get("task_key"),
                    "plan_version": version,
                    "required_materials": task.get("required_materials") or [],
                    "expected_output": task.get("expected_output"),
                },
                truth_status="observed",
                may_affect_real_metrics=False,
                metadata_json={
                    "task_key": task.get("task_key"),
                    "plan_version": version,
                    "plan_hash": confirmed_hash,
                    "task_version": 1,
                },
            )
            db.add(item)
        project.metadata_json = {
            **(meta or {}),
            "plan_status": "plan_confirmed",
            "plan_version": version,
            "plan_hash": confirmed_hash,
            "plan_confirmed_by": str(user.id),
            "plan_confirmed_at": now.isoformat(),
        }
        await self._audit(
            db, user, "project_plan_confirmed", "geo_project", str(project.id),
            reason=f"plan confirmed v{version}; not verified",
            metadata={"plan_version": version, "plan_hash": confirmed_hash},
            commit=False,
        )
        await self._audit(
            db, user, "project_tasks_generated", "geo_project", str(project.id),
            reason=f"generated {len(tasks)} tasks",
            metadata={"plan_version": version, "task_count": len(tasks)},
            commit=False,
        )
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        return await self.list_plan(db, user, project_id)

    async def update_task(
        self, db, user, project_id: str, task_id: str, data: Dict, expected_version: int = None,
    ) -> Dict:
        project = await self._require_project(db, project_id, lock=True)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm member permission required")
        meta = project.metadata_json or {}
        if meta.get("plan_status") not in ("plan_confirmed", "plan_active", "plan_completed"):
            raise PlanStateError(f"invalid_state_transition: {meta.get('plan_status', 'unknown')} -> task_update")
        if meta.get("plan_status") == "plan_completed":
            raise PlanStateError("plan_completed is terminal; task updates rejected")
        if expected_version is not None and int(expected_version) != (meta.get("plan_version") or 0):
            raise ValueError("计划版本已变化，请刷新后重试")
        item = await self._require_task(db, project.id, task_id, lock=True)
        if item.status == "completed":
            raise PlanStateError("completed task is terminal")
        progress = data.get("progress", item.progress)
        status = data.get("status", item.status)
        if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
            raise ValueError("progress must be between 0 and 100")
        if status not in ("planned", "in_progress", "blocked", "completed"):
            raise ValueError("invalid task status")
        expected_task_version = data.get("expected_task_version")
        current_task_version = (item.metadata_json or {}).get("task_version", 1)
        if expected_task_version is None or int(expected_task_version) != int(current_task_version):
            raise ValueError("任务版本已变化，请刷新后重试")
        if "progress" in data and "status" not in data:
            if item.status == "planned" and progress > 0:
                status = "in_progress"
            elif item.status == "in_progress" and progress == 100:
                status = "completed"
        if status == "planned" and progress != 0:
            raise ValueError("planned task must have progress 0")
        if status in ("in_progress", "blocked") and progress >= 100:
            raise ValueError("in_progress/blocked task must have progress 0-99")
        if status == "completed" and progress != 100:
            raise ValueError("completed task must have progress 100")
        allowed = {
            "planned": {"in_progress"},
            "in_progress": {"blocked", "completed"},
            "blocked": {"in_progress"},
            "completed": set(),
        }
        if status != item.status and status not in allowed.get(item.status, set()):
            raise PlanStateError(f"invalid_task_transition: {item.status} -> {status}")
        item.progress = progress
        item.status = status
        item.metadata_json = {
            **(item.metadata_json or {}),
            "task_version": int(current_task_version) + 1,
        }
        now = datetime.now(timezone.utc)
        if status == "in_progress" and meta.get("plan_status") == "plan_confirmed":
            project.metadata_json = {**meta, "plan_status": "plan_active", "plan_activated_at": now.isoformat()}
        tasks = (await db.execute(
            select(ProjectWorkItem).where(
                ProjectWorkItem.project_id == project.id,
                ProjectWorkItem.work_type == "plan_task",
            )
        )).scalars().all()
        if all(t.status == "completed" for t in tasks):
            project.metadata_json = {
                **(project.metadata_json or {}),
                "plan_status": "plan_completed",
                "plan_completed_at": now.isoformat(),
            }
        await self._audit(
            db, user, "project_task_updated", "project_work_item", str(item.id),
            reason=f"status={status} progress={progress}",
            metadata={"project_id": str(project.id), "plan_version": meta.get("plan_version")},
        )
        return await self.list_plan(db, user, project_id)

    async def _latest_artifact(self, db, project_id) -> Optional[ProjectArtifact]:
        return (await db.execute(
            select(ProjectArtifact)
            .where(ProjectArtifact.project_id == project_id, ProjectArtifact.artifact_type == "project_plan")
            .order_by(ProjectArtifact.created_at.desc())
            .limit(1)
        )).scalars().first()

    async def list_plan(self, db, user, project_id: str) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm member permission required")
        artifacts = (await db.execute(
            select(ProjectArtifact)
            .where(ProjectArtifact.project_id == project.id, ProjectArtifact.artifact_type == "project_plan")
            .order_by(ProjectArtifact.created_at.desc())
        )).scalars().all()
        tasks = (await db.execute(
            select(ProjectWorkItem)
            .where(ProjectWorkItem.project_id == project.id, ProjectWorkItem.work_type == "plan_task")
            .order_by(ProjectWorkItem.created_at.asc())
        )).scalars().all()
        now = datetime.now(timezone.utc)
        reminders = []
        task_rows = []
        for task in tasks:
            row = self._task_dict(task)
            row["reminders"] = self._reminders(task, now)
            reminders.extend(row["reminders"])
            task_rows.append(row)
        meta = project.metadata_json or {}
        return {
            "project": self._project_dict(project),
            "plan_status": meta.get("plan_status") or "project_created",
            "plan_version": meta.get("plan_version"),
            "plan_hash": meta.get("plan_hash"),
            "source_type": meta.get("source_type"),
            "source_id": meta.get("source_id"),
            "source_version": meta.get("source_version"),
            "positioning_version": meta.get("positioning_version"),
            "positioning_hash": meta.get("positioning_hash"),
            "profile_version": meta.get("profile_version"),
            "config_hash": meta.get("config_hash"),
            "versions": [self._artifact_dict(a) for a in artifacts],
            "draft_plan": artifacts[0].content_json if artifacts else None,
            "tasks": task_rows,
            "reminders": reminders,
            "workflow_sources": (await self.list_workflow_sources(db, user))["workflow_sources"],
            "unknown_items": (artifacts[0].content_json or {}).get("unknown_items", []) if artifacts else [],
            "can_edit": await self._control(db, user, str(project.realm_id)),
            "can_confirm": await self._confirm_permission(db, user, project),
            "can_update_task": (
                await self._control(db, user, str(project.realm_id))
                and (meta.get("plan_status") or "project_created") != "plan_completed"
            ),
            "generated_at": now.isoformat(),
        }

    def _project_dict(self, project: GeoProject) -> Dict:
        return {
            "id": str(project.id),
            "project_code": project.project_code,
            "realm_id": str(project.realm_id),
            "name": project.name,
            "objective": project.objective,
            "target_brand": project.target_brand,
            "target_product": project.target_product,
            "target_audience": project.target_audience,
            "scenario": project.scenario,
            "problems": project.problems or [],
            "status": project.status,
            "lifecycle_state": project.lifecycle_state,
            "truth_status": project.truth_status,
            "metadata_json": project.metadata_json or {},
            "created_at": project.created_at.isoformat() if project.created_at else None,
        }

    def _artifact_dict(self, artifact: ProjectArtifact) -> Dict:
        return {
            "id": str(artifact.id),
            "title": artifact.title,
            "artifact_type": artifact.artifact_type,
            "status": artifact.status,
            "truth_status": artifact.truth_status,
            "version": (artifact.metadata_json or {}).get("plan_version"),
            "plan_hash": (artifact.metadata_json or {}).get("plan_hash"),
            "content_json": artifact.content_json,
            "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
        }

    def _task_dict(self, task: ProjectWorkItem) -> Dict:
        return {
            "id": str(task.id),
            "task_key": (task.metadata_json or {}).get("task_key") or task.title,
            "phase": task.phase,
            "title": task.title,
            "purpose": task.purpose,
            "description": task.description,
            "expected_output": (task.input_manifest or {}).get("expected_output"),
            "acceptance_criteria": task.acceptance_criteria,
            "required_materials": task.required_materials or [],
            "owner_id": str(task.owner_id) if task.owner_id else None,
            "start_at": task.start_at.isoformat() if task.start_at else None,
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "reminder_at": task.reminder_at.isoformat() if task.reminder_at else None,
            "depends_on": task.depends_on or [],
            "risks": task.risks or [],
            "execution_mode": task.execution_mode,
            "progress": task.progress,
            "status": task.status,
            "truth_scope": task.truth_status,
            "task_version": (task.metadata_json or {}).get("task_version", 1),
        }

    @staticmethod
    def _reminders(item: ProjectWorkItem, now: datetime) -> List[Dict]:
        reminders = []
        if item.due_at and item.status not in ("completed",):
            if item.due_at < now:
                reminders.append({"type": "overdue", "message": "任务已逾期", "due_at": item.due_at.isoformat()})
            elif (item.due_at - now).days <= 3:
                reminders.append({"type": "due_soon", "message": "3 天内到期", "due_at": item.due_at.isoformat()})
        if item.reminder_at and item.reminder_at <= now and item.status not in ("completed",):
            reminders.append({"type": "reminder_due", "message": "提醒时间已到", "reminder_at": item.reminder_at.isoformat()})
        if item.status == "blocked":
            reminders.append({"type": "blocked", "message": "任务受阻，需要处理"})
        return reminders

    async def export_plan_csv(self, db, user, project_id: str) -> str:
        view = await self.list_plan(db, user, project_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "task_key", "phase", "title", "purpose", "status", "progress",
            "owner_id", "start_at", "due_at", "reminder_at", "depends_on",
            "risks", "acceptance_criteria", "execution_mode",
        ])
        for task in view["tasks"]:
            writer.writerow([
                task.get("task_key"), task.get("phase"), task.get("title"), task.get("purpose"),
                task.get("status"), task.get("progress"), task.get("owner_id") or "",
                task.get("start_at") or "", task.get("due_at") or "", task.get("reminder_at") or "",
                ";".join(task.get("depends_on") or []), ";".join(task.get("risks") or []),
                task.get("acceptance_criteria") or "", task.get("execution_mode") or "",
            ])
        project = await self._require_project(db, project_id)
        await self._audit(db, user, "project_plan_exported", "geo_project", str(project.id), reason="CSV export")
        return "\ufeff" + output.getvalue()


@lru_cache()
def get_project_plan_service() -> ProjectPlanService:
    return ProjectPlanService()
