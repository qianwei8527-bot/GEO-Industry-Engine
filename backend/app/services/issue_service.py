'''V10.6-R4 issue closed-loop service.'''

import hashlib
import json
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Dict, List

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geo_project import GeoProject, ProjectArtifact, ProjectWorkItem
from app.models.governance import NodeMembership
from app.models.issue import IssueRecord, IssueEvent
from app.models.realm import RealmRegistry
from app.models.user import User
from app.services.governance import get_governance_service
from app.services.realm_service import get_realm_service


class IssueStateError(Exception):
    pass


ALLOWED_TRANSITIONS = {
    "open": {"triaged", "cancelled"},
    "triaged": {"in_progress", "cancelled"},
    "in_progress": {"resolved", "cancelled"},
    "resolved": {"in_progress", "verified"},
    "verified": set(),
    "cancelled": set(),
}

CONFIRM_ROLES = {"node_owner", "node_reviewer"}

CATEGORY_KEYWORDS = {
    "资料与数据": ["资料", "文档", "数据", "证据", "文件"],
    "流程与协作": ["流程", "审批", "协作", "对接", "确认", "同步"],
    "工具与执行": ["工具", "执行", "接口", "平台", "系统", "脚本"],
    "权限与合规": ["权限不足", "权限", "合规", "授权", "风险", "隐私"],
    "渠道与传播": ["渠道", "发布", "传播", "内容", "推广"],
    "外部沟通": ["客户", "供应商", "外部", "联系", "合作"],
}


def _canonical(data) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


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


class IssueService:
    def __init__(self):
        self.realm_service = get_realm_service()
        self.gov = get_governance_service()

    async def _control(self, db, user, realm_id) -> bool:
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError("realm not found")
        return await self.realm_service._control(db, user, str(registry.entity_id))

    async def _confirm_permission(self, db, user, realm_id) -> bool:
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError("realm not found")
        if self.gov.is_system_admin(user):
            return True
        roles = await self.gov.get_node_roles(db, user.id, str(registry.entity_id))
        return bool(set(roles) & CONFIRM_ROLES)

    async def _audit(self, db, user, action, target_type, target_id, reason=None, metadata=None, commit: bool = True):
        await self.gov.audit(
            db, user.id, action, target_type, target_id,
            reason=reason, actor_label=user.name, metadata=metadata, commit=commit,
        )

    async def _next_event_version(self, db, issue_id) -> int:
        value = (await db.execute(
            select(func.max(IssueEvent.event_version)).where(IssueEvent.issue_id == issue_id)
        )).scalar()
        return int(value or 0) + 1

    async def _event(self, db, user, issue_id, event_type, content, metadata=None, version=None):
        row = IssueEvent(
            issue_id=issue_id,
            event_version=version if version is not None else await self._next_event_version(db, issue_id),
            event_type=event_type,
            actor_id=user.id,
            actor_label=user.name,
            content=content,
            metadata_json=metadata,
        )
        db.add(row)
        return row

    async def _commit(self, db):
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    async def _require_issue(self, db, issue_id, lock: bool = False) -> IssueRecord:
        try:
            issue_uuid = uuid.UUID(str(issue_id))
        except (ValueError, TypeError):
            raise ValueError("issue_id must be a valid UUID")
        if lock:
            rows = (await db.execute(
                select(IssueRecord).where(IssueRecord.id == issue_uuid).with_for_update()
            )).scalars().all()
            issue = rows[0] if rows else None
        else:
            issue = await db.get(IssueRecord, issue_uuid)
        if not issue:
            raise ValueError("issue not found")
        return issue

    async def _require_artifact(self, db, artifact_id, lock: bool = False) -> ProjectArtifact:
        try:
            artifact_uuid = uuid.UUID(str(artifact_id))
        except (ValueError, TypeError):
            raise ValueError("artifact not found")
        if lock:
            rows = (await db.execute(
                select(ProjectArtifact).where(ProjectArtifact.id == artifact_uuid).with_for_update()
            )).scalars().all()
            artifact = rows[0] if rows else None
        else:
            artifact = await db.get(ProjectArtifact, artifact_uuid)
        if not artifact:
            raise ValueError("artifact not found")
        return artifact

    @staticmethod
    def _assert_transition(current: str, new: str):
        if new not in ALLOWED_TRANSITIONS.get(current, set()):
            raise IssueStateError(f"invalid_issue_transition: {current} -> {new}")

    async def _permissions(self, db, user, issue) -> Dict[str, bool]:
        control = await self._control(db, user, str(issue.realm_id))
        owner = await self._confirm_permission(db, user, str(issue.realm_id))
        terminal = issue.status in ("verified", "cancelled")
        return {
            "can_create_issue": control,
            "can_triage": control and issue.status == "open",
            "can_update_issue": control and not terminal,
            "can_add_attempt": control and issue.status in ("open", "triaged", "in_progress", "resolved"),
            "can_resolve": control and issue.status == "in_progress",
            "can_verify": owner and issue.status == "resolved",
            "can_generate_skill": control and issue.status == "verified",
            "can_confirm_skill": owner,
        }

    @staticmethod
    def _classify(text: str) -> Dict:
        best_category = None
        best_length = -1
        best_hits = []
        for cat, keywords in CATEGORY_KEYWORDS.items():
            hits = [kw for kw in keywords if kw in (text or "")]
            if not hits:
                continue
            max_len = max(len(kw) for kw in hits)
            if max_len > best_length:
                best_category = cat
                best_length = max_len
                best_hits = hits
        input_hash = hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:32]
        if best_category:
            output = {
                "category": best_category,
                "impact_stage": "execution",
                "severity": "normal",
                "possible_causes": [],
                "suggested_next": "域主复核分类后进入处理",
                "confidence": 0.8,
                "basis": "关键词命中：" + "、".join(best_hits[:5]),
                "engine": "rule_based",
                "engine_version": "1.0.0",
                "input_hash": input_hash,
                "truth_scope": "inferred",
            }
        else:
            output = {
                "category": "其他",
                "impact_stage": "unknown",
                "severity": "normal",
                "possible_causes": [],
                "suggested_next": "域主补充上下文并指定分类",
                "confidence": 0.45,
                "basis": "未命中关键词，建议域主复核",
                "engine": "rule_based",
                "engine_version": "1.0.0",
                "input_hash": input_hash,
                "truth_scope": "inferred",
            }
        output["output_hash"] = hashlib.sha256(_canonical(output).encode("utf-8")).hexdigest()[:32]
        return output

    async def create_issue(self, db, user, realm_id, data: Dict) -> Dict:
        if not await self._control(db, user, realm_id):
            raise PermissionError("realm member permission required")
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError("realm not found")
        idempotency_key = (data.get("idempotency_key") or "").strip()
        original = (data.get("original_text") or "").strip()
        if not original:
            raise ValueError("original_text is required")
        requested_truth_scope = (data.get("truth_scope") or "observed").strip()
        if requested_truth_scope != "observed":
            raise ValueError("truth_scope 仅允许 observed")
        project = None
        if data.get("project_id"):
            project = await db.get(GeoProject, uuid.UUID(str(data["project_id"])))
            if not project or str(project.realm_id) != str(registry.id):
                raise ValueError("project does not belong to this realm")
        work_item = None
        if data.get("work_item_id"):
            work_item = await db.get(ProjectWorkItem, uuid.UUID(str(data["work_item_id"])))
            if not work_item or work_item.work_type != "plan_task":
                raise ValueError("source work item must be a plan_task")
            if project and str(work_item.project_id) != str(project.id):
                raise ValueError("work item does not belong to this project")
            if not project:
                project = await db.get(GeoProject, work_item.project_id)
                if not project or str(project.realm_id) != str(registry.id):
                    raise ValueError("work item does not belong to this realm")
        classification = self._classify(original)
        project_id_value = project.id if project else None
        work_item_id_value = work_item.id if work_item else None
        idempotency_scope = (
            hashlib.sha256(
                f"{registry.id}:{project_id_value or ''}:{work_item_id_value or ''}:{idempotency_key}".encode("utf-8")
            ).hexdigest()
            if idempotency_key
            else None
        )
        if idempotency_scope:
            existing = (await db.execute(
                select(IssueRecord).where(
                    IssueRecord.realm_id == registry.id,
                    IssueRecord.idempotency_key == idempotency_scope,
                )
            )).scalars().first()
            if existing:
                return self._issue_dict(existing, await self._events_for(db, existing.id), await self._permissions(db, user, existing))
        issue = IssueRecord(
            issue_code=f"ISS-{uuid.uuid4().hex[:12].upper()}",
            realm_id=registry.id,
            project_id=project.id if project else None,
            work_item_id=work_item.id if work_item else None,
            original_text=original,
            title=(data.get("title") or original[:80]).strip(),
            client_ref=data.get("client_ref"),
            scenario=data.get("scenario"),
            impact=data.get("impact"),
            urgency=data.get("urgency") or "normal",
            source=(data.get("source") or "manual").strip(),
            source_type=(data.get("source_type") or "owner_manual").strip(),
            truth_scope="observed",
            severity=(data.get("severity") or "normal").strip(),
            status="open",
            version=1,
            idempotency_key=idempotency_scope,
            classification_status="suggested",
            evidence_ids=data.get("evidence_ids") or [],
            ai_classification=classification,
            assignee_id=uuid.UUID(str(data["assignee_id"])) if data.get("assignee_id") else None,
            created_by=user.id,
        )
        db.add(issue)
        await db.flush()
        await self._event(db, user, issue.id, "created", original)
        await self._event(
            db, user, issue.id, "ai_classified",
            f"规则分类建议：{classification.get('category')}",
            {"confidence": classification.get("confidence"), "basis": classification.get("basis")},
        )
        try:
            await self._commit(db)
        except IntegrityError:
            await db.rollback()
            if idempotency_scope:
                existing = (await db.execute(
                    select(IssueRecord).where(
                        IssueRecord.realm_id == registry.id,
                        IssueRecord.idempotency_key == idempotency_scope,
                    )
                )).scalars().first()
                if existing:
                    return self._issue_dict(existing, await self._events_for(db, existing.id), await self._permissions(db, user, existing))
            raise
        await db.refresh(issue)
        await self._audit(db, user, "issue_created", "issue_record", str(issue.id), reason=issue.issue_code)
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def list_issues(self, db, user, realm_id, project_id=None, status=None, include_events=False) -> List[Dict]:
        if not await self._control(db, user, realm_id):
            raise PermissionError("realm member permission required")
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError("realm not found")
        query = select(IssueRecord).where(IssueRecord.realm_id == registry.id)
        if project_id:
            query = query.where(IssueRecord.project_id == uuid.UUID(str(project_id)))
        if status:
            query = query.where(IssueRecord.status == status)
        query = query.order_by(IssueRecord.updated_at.desc())
        rows = (await db.execute(query)).scalars().all()
        result = []
        for issue in rows:
            events = []
            if include_events:
                events = await self._events_for(db, issue.id)
            result.append(self._issue_dict(issue, events, await self._permissions(db, user, issue)))
        return result

    async def get_issue(self, db, user, issue_id) -> Dict:
        issue = await self._require_issue(db, issue_id)
        if not await self._control(db, user, str(issue.realm_id)):
            raise PermissionError("realm member permission required")
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def update_issue(self, db, user, issue_id, data: Dict, expected_version: int = None) -> Dict:
        issue = await self._require_issue(db, issue_id, lock=True)
        if not await self._control(db, user, str(issue.realm_id)):
            raise PermissionError("realm member permission required")
        if issue.status in ("verified", "cancelled"):
            raise IssueStateError("issue is terminal")
        if expected_version is None or int(expected_version) != issue.version:
            raise ValueError("问题版本已变化，请刷新后重试")
        before = issue.status
        if data.get("status"):
            if data["status"] == "verified":
                raise ValueError("verified 只能通过专用验证接口完成")
            self._assert_transition(issue.status, data["status"])
            issue.status = data["status"]
        if data.get("truth_scope") and data["truth_scope"] not in ("observed",):
            raise ValueError("truth_scope 仅允许 observed；verified 必须由可信验证机制产生")
        before_category = issue.category
        scalar_fields = {
            "title", "client_ref", "scenario", "impact", "urgency", "source", "source_type",
            "category", "severity", "possible_causes", "final_solution", "applicability_boundary",
            "truth_scope",
        }
        for key, value in (data or {}).items():
            if key in scalar_fields and value is not None:
                setattr(issue, key, str(value).strip() or None)
            elif key == "assignee_id" and value:
                issue.assignee_id = uuid.UUID(str(value))
            elif key == "due_at":
                issue.due_at = _parse_dt(value)
        classification_fields = {"category", "severity", "possible_causes"}
        if any(key in (data or {}) for key in classification_fields):
            if issue.classification_status == "confirmed":
                issue.classification_status = "suggested"
                await self._event(
                    db, user, issue.id, "classification_reopened",
                    "域主修改分类字段，需重新确认",
                    {"issue_version": issue.version + 1},
                )
            if data.get("category") is not None and str(data.get("category")) != before_category:
                await self._event(
                    db, user, issue.id, "category_updated",
                    f"分类修改为：{data.get('category')}",
                    {"issue_version": issue.version + 1},
                )
        issue.version += 1
        if issue.status == "resolved":
            issue.resolved_by = user.id
            issue.resolved_at = datetime.now(timezone.utc)
        if before != issue.status:
            await self._event(
                db, user, issue.id, "status_changed",
                f"{before} -> {issue.status}",
                {"from": before, "to": issue.status, "issue_version": issue.version},
            )
        if data.get("final_solution"):
            await self._event(
                db, user, issue.id, "solution_recorded",
                str(data.get("final_solution")),
                {"issue_version": issue.version},
            )
        await self._commit(db)
        await db.refresh(issue)
        await self._audit(db, user, "issue_updated", "issue_record", str(issue.id), reason=f"version {issue.version}")
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def classify_issue(self, db, user, issue_id, expected_version: int = None) -> Dict:
        issue = await self._require_issue(db, issue_id, lock=True)
        if not await self._control(db, user, str(issue.realm_id)):
            raise PermissionError("realm member permission required")
        if issue.status in ("verified", "cancelled"):
            raise IssueStateError("终态问题禁止重新分类")
        if expected_version is None or int(expected_version) != issue.version:
            raise ValueError("问题版本已变化，请刷新后重试")
        classification = self._classify(issue.original_text)
        issue.ai_classification = classification
        issue.classification_status = "suggested"
        issue.version += 1
        await self._event(
            db, user, issue.id, "ai_classified",
            f"规则分类建议：{classification.get('category')}",
            {"confidence": classification.get("confidence"), "basis": classification.get("basis")},
        )
        await self._commit(db)
        await db.refresh(issue)
        await self._audit(db, user, "issue_classified", "issue_record", str(issue.id), reason="rule_based suggestion")
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def confirm_classification(self, db, user, issue_id, expected_version: int = None) -> Dict:
        issue = await self._require_issue(db, issue_id, lock=True)
        if issue.status in ("verified", "cancelled"):
            raise IssueStateError("终态问题禁止确认分类")
        if not await self._confirm_permission(db, user, str(issue.realm_id)):
            raise PermissionError("分类确认需要域主或专业审核角色")
        if not issue.category or not str(issue.category).strip():
            raise ValueError("category 不能为空")
        if expected_version is None or int(expected_version) != issue.version:
            raise ValueError("问题版本已变化，请刷新后重试")
        issue.classification_status = "confirmed"
        issue.version += 1
        await self._event(
            db, user, issue.id, "classification_confirmed",
            f"分类已由域主确认：{issue.category or '其他'}",
            {"issue_version": issue.version, "category": issue.category},
        )
        await self._commit(db)
        await db.refresh(issue)
        await self._audit(db, user, "issue_classification_confirmed", "issue_record", str(issue.id), reason=issue.category)
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def add_attempt(self, db, user, issue_id, data: Dict, expected_version: int = None) -> Dict:
        issue = await self._require_issue(db, issue_id, lock=True)
        if not await self._control(db, user, str(issue.realm_id)):
            raise PermissionError("realm member permission required")
        if issue.status in ("verified", "cancelled"):
            raise IssueStateError("issue is terminal")
        if expected_version is None or int(expected_version) != issue.version:
            raise ValueError("问题版本已变化，请刷新后重试")
        method = (data.get("method") or "").strip()
        if not method:
            raise ValueError("method is required")
        attempt = {
            "method": method,
            "action": data.get("action"),
            "tool": data.get("tool"),
            "owner_id": str(user.id),
            "started_at": data.get("started_at"),
            "ended_at": data.get("ended_at"),
            "result": data.get("result", "failed"),
            "failure_reason": data.get("failure_reason"),
            "evidence_refs": data.get("evidence_refs") or [],
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        issue.version += 1
        await self._event(
            db, user, issue.id, "attempt", f"处理尝试：{method}",
            {"attempt": attempt, "issue_version": issue.version},
        )
        await self._commit(db)
        await db.refresh(issue)
        await self._audit(db, user, "issue_attempt_added", "issue_record", str(issue.id), reason=method)
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def resolve_issue(self, db, user, issue_id, expected_version: int = None) -> Dict:
        issue = await self._require_issue(db, issue_id, lock=True)
        if not await self._control(db, user, str(issue.realm_id)):
            raise PermissionError("realm member permission required")
        if expected_version is None or int(expected_version) != issue.version:
            raise ValueError("问题版本已变化，请刷新后重试")
        self._assert_transition(issue.status, "resolved")
        issue.status = "resolved"
        issue.resolved_by = user.id
        issue.resolved_at = datetime.now(timezone.utc)
        issue.version += 1
        await self._event(
            db, user, issue.id, "resolved", "问题已解决，等待域主验证",
            {"issue_version": issue.version},
        )
        await self._commit(db)
        await db.refresh(issue)
        await self._audit(db, user, "issue_resolved", "issue_record", str(issue.id), reason="resolved")
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def verify_issue(self, db, user, issue_id, expected_version: int = None) -> Dict:
        issue = await self._require_issue(db, issue_id, lock=True)
        if not await self._control(db, user, str(issue.realm_id)):
            raise PermissionError("realm member permission required")
        if not await self._confirm_permission(db, user, str(issue.realm_id)):
            raise PermissionError("issue verify requires realm owner")
        if expected_version is None or int(expected_version) != issue.version:
            raise ValueError("问题版本已变化，请刷新后重试")
        self._assert_transition(issue.status, "verified")
        issue.status = "verified"
        issue.verified_by = user.id
        issue.verified_at = datetime.now(timezone.utc)
        issue.version += 1
        await self._event(
            db, user, issue.id, "verified", "域主已验证问题；不自动改变原任务状态",
            {"issue_version": issue.version, "verified_by": str(user.id)},
        )
        await self._commit(db)
        await db.refresh(issue)
        await self._audit(db, user, "issue_verified", "issue_record", str(issue.id), reason="verified")
        return self._issue_dict(issue, await self._events_for(db, issue.id), await self._permissions(db, user, issue))

    async def generate_skill(self, db, user, issue_ids: List[str]) -> Dict:
        if not issue_ids:
            raise ValueError("issue_ids 不能为空")
        issues = []
        for issue_id in issue_ids:
            issues.append(await self._require_issue(db, issue_id, lock=True))
        realms = {str(issue.realm_id) for issue in issues}
        if len(realms) != 1:
            raise ValueError("跨 Realm 问题不能合并生成 Skill")
        project_ids = {str(issue.project_id) for issue in issues if issue.project_id}
        if len(project_ids) != 1 or not project_ids:
            raise ValueError("Skill 草稿必须来自同一项目")
        for issue in issues:
            if not await self._control(db, user, str(issue.realm_id)):
                raise PermissionError("realm member permission required")
            if issue.status != "verified":
                raise ValueError("只有已验证问题可以生成 Skill 草稿")
        realm_id = issues[0].realm_id
        project_id = issues[0].project_id
        final_solutions = [issue.final_solution for issue in issues if issue.final_solution]
        boundaries = [issue.applicability_boundary for issue in issues if issue.applicability_boundary]
        evidence_refs = []
        for issue in issues:
            evidence_refs.extend(issue.evidence_ids or [])
        attempts = []
        for issue in issues:
            for event in await self._events_for(db, issue.id):
                if event["event_type"] == "attempt":
                    attempt_meta = (event["metadata"] or {}).get("attempt") or {}
                    attempts.append({
                        "issue_id": str(issue.id),
                        "event_id": event["id"],
                        "attempt": attempt_meta,
                    })
        successful_attempts = [a for a in attempts if (a.get("attempt") or {}).get("result") in ("success", "partial")]
        failed_attempts = [a for a in attempts if (a.get("attempt") or {}).get("result") == "failed"]
        tools = list({(a.get("attempt") or {}).get("tool") for a in attempts if (a.get("attempt") or {}).get("tool")})
        steps = [{"action": "确认问题场景", "owner": "域主"}]
        for attempt in successful_attempts:
            attempt_meta = attempt.get("attempt") or {}
            steps.append({
                "action": attempt_meta.get("action") or attempt_meta.get("method") or "按已验证方案执行",
                "owner": "负责人",
                "tool": attempt_meta.get("tool"),
            })
        common_failures = [{"failure": a.get("attempt", {}).get("failure_reason") or "未知失败"} for a in failed_attempts]
        skill = {
            "name": "问题处理 Skill 草稿",
            "applicable_scenario": "同类执行问题复用处理方法",
            "trigger_condition": "出现与来源问题相似场景",
            "prerequisite": "域主确认问题与历史匹配",
            "inputs": [],
            "steps": steps,
            "tools": tools,
            "expected_output": final_solutions[0] if final_solutions else "可执行处理方案",
            "validation_criteria": "域主验证通过",
            "common_failures": common_failures,
            "prohibited_usage": (boundaries[0] if boundaries else None) or "未经域主确认不得执行或发布",
            "source_issues": [str(i.id) for i in issues],
            "source_attempts": attempts,
            "final_solutions": final_solutions,
            "applicability_boundaries": boundaries,
            "evidence_refs": [str(e) for e in evidence_refs],
            "provenance": "r4_issue_closed_loop",
            "version": 1,
            "owner_confirmed": False,
            "truth_scope": "inferred",
        }
        skill_hash = hashlib.sha256(_canonical(skill).encode("utf-8")).hexdigest()[:32]
        skill["source_hash"] = skill_hash
        artifact = ProjectArtifact(
            project_id=project_id,
            artifact_type="business_skill_draft",
            title=skill["name"],
            content_json=skill,
            status="draft",
            operator_id=user.id,
            truth_status="inferred",
            may_affect_real_metrics=False,
            metadata_json={
                "realm_id": str(realm_id),
                "project_id": str(project_id),
                "source_issues": [str(i.id) for i in issues],
                "owner_confirmed": False,
                "truth_scope": "inferred",
                "version": 1,
                "skill_hash": skill_hash,
            },
        )
        db.add(artifact)
        await self._commit(db)
        await db.refresh(artifact)
        await self._audit(db, user, "business_skill_draft_generated", "project_artifact", str(artifact.id), reason="draft")
        return self._artifact_dict(artifact)

    async def confirm_skill(self, db, user, artifact_id, confirmed: bool = False) -> Dict:
        artifact = await self._require_artifact(db, artifact_id)
        if artifact.artifact_type != "business_skill_draft":
            raise ValueError("artifact is not a business skill draft")
        realm_id = (artifact.metadata_json or {}).get("realm_id") or ""
        if not await self._control(db, user, realm_id):
            raise PermissionError("realm member permission required")
        if not await self._confirm_permission(db, user, realm_id):
            raise PermissionError("skill confirm requires realm owner")
        if not confirmed:
            artifact.status = "rejected"
            artifact.metadata_json = {**(artifact.metadata_json or {}), "owner_confirmed": False}
        else:
            artifact.status = "confirmed"
            artifact.metadata_json = {
                **(artifact.metadata_json or {}),
                "owner_confirmed": True,
                "confirmed_by": str(user.id),
                "confirmed_at": datetime.now(timezone.utc).isoformat(),
            }
        await self._commit(db)
        await db.refresh(artifact)
        await self._audit(db, user, "business_skill_draft_confirmed", "project_artifact", str(artifact.id), reason=str(confirmed))
        return self._artifact_dict(artifact)

    async def update_skill_draft(self, db, user, artifact_id, edits: Dict, expected_version: int = None) -> Dict:
        artifact = await self._require_artifact(db, artifact_id, lock=True)
        if artifact.artifact_type != "business_skill_draft":
            raise ValueError("artifact is not a business skill draft")
        if artifact.status != "draft":
            raise IssueStateError("只有 draft 状态的 Skill 草稿可编辑")
        realm_id = (artifact.metadata_json or {}).get("realm_id") or ""
        if not await self._control(db, user, realm_id):
            raise PermissionError("realm member permission required")
        current_version = int((artifact.metadata_json or {}).get("version") or 1)
        if expected_version is None or int(expected_version) != current_version:
            raise ValueError("Skill 草稿版本已变化，请刷新后重试")
        content = dict(artifact.content_json or {})
        allowed_keys = {
            "name", "applicable_scenario", "trigger_condition", "prerequisite",
            "inputs", "steps", "tools", "expected_output", "validation_criteria",
            "common_failures", "prohibited_usage", "final_solutions",
            "applicability_boundaries", "evidence_refs",
        }
        forbidden = [key for key in (edits or {}) if key not in allowed_keys]
        if forbidden:
            raise ValueError(f"禁止修改字段：{', '.join(sorted(forbidden))}")
        for key, value in (edits or {}).items():
            content[key] = value
        content["version"] = current_version + 1
        content["source_hash"] = hashlib.sha256(_canonical(content).encode("utf-8")).hexdigest()[:32]
        content["truth_scope"] = "inferred"
        content["owner_confirmed"] = False
        content["provenance"] = "r4_issue_closed_loop"
        artifact.content_json = content
        artifact.metadata_json = {
            **(artifact.metadata_json or {}),
            "version": current_version + 1,
            "skill_hash": content["source_hash"],
            "owner_confirmed": False,
            "truth_scope": "inferred",
        }
        await self._commit(db)
        await db.refresh(artifact)
        await self._audit(db, user, "business_skill_draft_updated", "project_artifact", str(artifact.id), reason=f"version {current_version + 1}")
        return self._artifact_dict(artifact)

    async def list_skill_drafts(self, db, user, realm_id: str, project_id: str = None) -> List[Dict]:
        if not await self._control(db, user, realm_id):
            raise PermissionError("realm member permission required")
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError("realm not found")
        query = (
            select(ProjectArtifact)
            .join(GeoProject, GeoProject.id == ProjectArtifact.project_id)
            .where(
                ProjectArtifact.artifact_type == "business_skill_draft",
                GeoProject.realm_id == registry.id,
            )
        )
        if project_id:
            query = query.where(ProjectArtifact.project_id == uuid.UUID(str(project_id)))
        query = query.order_by(ProjectArtifact.created_at.desc())
        rows = (await db.execute(query)).scalars().all()
        return [self._artifact_dict(artifact) for artifact in rows]

    async def list_realm_members(self, db, user, realm_id: str) -> List[Dict]:
        if not await self._control(db, user, realm_id):
            raise PermissionError("realm member permission required")
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError("realm not found")
        rows = (await db.execute(
            select(User)
            .join(NodeMembership, NodeMembership.user_id == User.id)
            .where(
                NodeMembership.node_id == str(registry.entity_id),
                NodeMembership.status == "active",
            )
            .order_by(User.name.asc())
        )).scalars().all()
        return [{"id": str(user.id), "name": user.name, "email": user.email} for user in rows]

    async def _events_for(self, db, issue_id) -> List[Dict]:
        rows = (await db.execute(
            select(IssueEvent)
            .where(IssueEvent.issue_id == issue_id)
            .order_by(IssueEvent.event_version.asc())
        )).scalars().all()
        return [self._event_dict(e) for e in rows]

    def _issue_dict(self, issue, events, permissions) -> Dict:
        return {
            "id": str(issue.id),
            "issue_code": issue.issue_code,
            "realm_id": str(issue.realm_id),
            "project_id": str(issue.project_id) if issue.project_id else None,
            "work_item_id": str(issue.work_item_id) if issue.work_item_id else None,
            "idempotency_key": issue.idempotency_key,
            "original_text": issue.original_text,
            "title": issue.title,
            "client_ref": issue.client_ref,
            "scenario": issue.scenario,
            "impact": issue.impact,
            "urgency": issue.urgency,
            "source": issue.source,
            "source_type": issue.source_type,
            "truth_scope": issue.truth_scope,
            "category": issue.category,
            "severity": issue.severity,
            "status": issue.status,
            "version": issue.version,
            "classification_status": issue.classification_status,
            "possible_causes": issue.possible_causes,
            "tried_methods": issue.tried_methods or [],
            "effective_methods": issue.effective_methods or [],
            "ineffective_methods": issue.ineffective_methods or [],
            "final_solution": issue.final_solution,
            "evidence_ids": issue.evidence_ids or [],
            "applicability_boundary": issue.applicability_boundary,
            "assignee_id": str(issue.assignee_id) if issue.assignee_id else None,
            "due_at": issue.due_at.isoformat() if issue.due_at else None,
            "recurrence_count": issue.recurrence_count,
            "is_template_candidate": issue.is_template_candidate,
            "template_status": issue.template_status,
            "ai_classification": issue.ai_classification,
            "created_by": str(issue.created_by) if issue.created_by else None,
            "resolved_by": str(issue.resolved_by) if issue.resolved_by else None,
            "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None,
            "verified_by": str(issue.verified_by) if issue.verified_by else None,
            "verified_at": issue.verified_at.isoformat() if issue.verified_at else None,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
            "events": events,
            "permissions": permissions,
        }

    @staticmethod
    def _event_dict(event: IssueEvent) -> Dict:
        return {
            "id": str(event.id),
            "issue_id": str(event.issue_id),
            "event_version": event.event_version,
            "event_type": event.event_type,
            "actor_id": str(event.actor_id) if event.actor_id else None,
            "actor_label": event.actor_label,
            "content": event.content,
            "metadata": event.metadata_json,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }

    @staticmethod
    def _artifact_dict(artifact: ProjectArtifact) -> Dict:
        return {
            "id": str(artifact.id),
            "project_id": str(artifact.project_id),
            "artifact_type": artifact.artifact_type,
            "title": artifact.title,
            "status": artifact.status,
            "truth_status": artifact.truth_status,
            "content_json": artifact.content_json,
            "metadata_json": artifact.metadata_json or {},
            "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
        }


@lru_cache()
def get_issue_service() -> IssueService:
    return IssueService()
