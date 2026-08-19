"""V10-P0 GEO Project service.

Project is the real demand-to-result converter for a Realm owner. This
service intentionally does not change Reputation or Law state.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import urlparse

import yaml
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.realm import RealmRegistry, RealmDataAsset, RealmDataAuthorization
from app.models.geo_project import (
    GeoProject,
    ProjectWorkItem,
    ProjectArtifact,
    ToolExecutionRecord,
    ProjectOutcome,
)
from app.models.evidence_claim import EvidenceClaim
from app.models.evidence import Evidence
from app.models.intake import ClientIntake, IntakeAnalysis
from app.services.intake_service import IntakeStateTransitionError
from app.services.local_tool_adapter import run_local_tool
from app.services.observation_network import validate_url, resolve_all_and_validate
from app.services.governance import get_governance_service
from app.services.realm_service import get_realm_service


def _load_project_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "config", "universe", "geo_project.yaml",
    )
    if os.path.exists(p):
        raw = open(p, encoding="utf-8").read()
        data = yaml.safe_load(raw) or {}
        data["config_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return data
    return {"version": "1.0.0", "config_hash": "missing"}


class GeoProjectService:
    def __init__(self):
        self.config = _load_project_config()
        self.realm_service = get_realm_service()

    async def _control(self, db: AsyncSession, user, realm_id: str) -> bool:
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError('realm not found')
        return await self.realm_service._control(db, user, str(registry.entity_id))

    async def _audit(self, db, user, action, target_type, target_id, reason=None, metadata=None, commit: bool = True):
        await get_governance_service().audit(
            db, user.id, action, target_type, target_id,
            reason=reason, actor_label=user.name, metadata=metadata,
            commit=commit,
        )

    async def _create_project_row(self, db: AsyncSession, user, data: Dict, commit: bool = False) -> Dict:
        realm_id = data.get("realm_id")
        name = (data.get("name") or "").strip()
        if not realm_id or not name:
            raise ValueError("realm_id and name are required")
        if not await self._control(db, user, realm_id):
            raise PermissionError("realm owner/editor permission required")
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError('realm not found')
        truth_status = (data.get("truth_status") or "observed").strip()
        if truth_status not in ("observed", "synthetic"):
            raise ValueError("project truth_status must be observed or synthetic")
        project = GeoProject(
            project_code=data.get("project_code") or f"GEO-P-{uuid.uuid4().hex[:10].upper()}",
            realm_id=registry.id,
            realm_entity_id=registry.entity_id,
            project_type=data.get("project_type", "geo"),
            name=name,
            objective=data.get("objective"),
            target_brand=data.get("target_brand"),
            target_product=data.get("target_product"),
            target_audience=data.get("target_audience"),
            scenario=data.get("scenario"),
            problems=data.get("problems") or [],
            ai_platforms=data.get("ai_platforms") or [],
            question_set=data.get("question_set") or [],
            competitors=data.get("competitors") or [],
            expected_outcome=data.get("expected_outcome"),
            lifecycle_state="registered",
            status="draft",
            operator_id=user.id,
            source=data.get("source", "realm_owner"),
            truth_status=truth_status,
            may_affect_real_metrics=False,
            metadata_json={
                **(data.get("metadata") or {}),
                "simulation": truth_status == "synthetic",
            },
        )
        db.add(project)
        await db.flush()
        await db.refresh(project)
        await self._audit(db, user, "geo_project_created", "geo_project", str(project.id),
                          reason=project.project_code, commit=commit)
        return self._project_dict(project)

    async def create_project(self, db: AsyncSession, user, data: Dict) -> Dict:
        return await self._create_project_row(db, user, data, commit=True)

    async def create_project_from_positioning(
        self,
        db: AsyncSession,
        user,
        intake_id: str,
        confirmed: bool = False,
        expected_position_version: int = None,
    ) -> Dict:
        try:
            intake_uuid = uuid.UUID(str(intake_id))
        except (ValueError, TypeError):
            raise ValueError("intake_id must be a valid UUID")
        intake = (await db.execute(
            select(ClientIntake)
            .where(ClientIntake.id == intake_uuid)
            .with_for_update()
        )).scalars().first()
        if not intake:
            raise ValueError("intake not found")
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        if not confirmed:
            raise ValueError("显式确认后才能创建项目")
        await db.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
            {"key": f"positioning_project:{intake.id}"},
        )
        existing = await self._find_positioning_project(db, intake)
        if existing:
            return await self._repair_or_reject_existing(
                db, user, intake, existing, expected_position_version
            )
        meta = intake.metadata_json or {}
        if meta.get("flow_status") != "positioning_confirmed":
            raise IntakeStateTransitionError(
                f"invalid_state_transition: {meta.get('flow_status', 'unknown')} -> project_created"
            )
        if meta.get("positioning_status") != "confirmed":
            raise ValueError("定位尚未确认")
        if expected_position_version is not None and meta.get("positioning_version") != expected_position_version:
            raise ValueError("定位版本已变化，请刷新后重试")
        latest = (await db.execute(
            select(IntakeAnalysis)
            .where(IntakeAnalysis.intake_id == intake.id)
            .order_by(IntakeAnalysis.version.desc())
            .limit(1)
        )).scalars().first()
        positioning = (latest.analysis_json or {}).get("positioning") or {}
        conclusion = positioning.get("conclusion") or {}
        project_code = f"GEO-P-{uuid.uuid5(uuid.NAMESPACE_URL, f'positioning:{intake.id}').hex.upper()}"
        try:
            project = await self._create_project_row(db, user, {
                "project_code": project_code,
                "realm_id": str(intake.realm_id),
                "name": f"{conclusion.get('who_we_are') or '客户'}定位项目",
                "objective": conclusion.get("priority_direction") or conclusion.get("main_gap") or "进入项目与计划",
                "target_brand": conclusion.get("who_we_are"),
                "target_product": conclusion.get("provide"),
                "target_audience": conclusion.get("serve_who"),
                "scenario": "positioning_handoff",
                "problems": [conclusion.get("solve_problem")] if conclusion.get("solve_problem") else [],
                "truth_status": "observed",
                "metadata": {
                    "source": "positioning_handoff",
                    "intake_id": str(intake.id),
                    "profile_version": meta.get("profile_version"),
                    "positioning_version": meta.get("positioning_version"),
                    "positioning_status": "confirmed",
                    "positioning_hash": positioning.get("positioning_hash"),
                    "rule_version": positioning.get("rule_version"),
                    "config_hash": positioning.get("config_hash"),
                    "positioning_summary": conclusion,
                },
            }, commit=False)
        except IntegrityError:
            await db.rollback()
            return await self._resolve_existing_after_conflict(
                db, user, intake_id, project_code, expected_position_version
            )
        intake.metadata_json = {
            **(intake.metadata_json or {}),
            "flow_status": "project_created",
            "project_id": project["id"],
        }
        await self._audit(
            db, user, "project_handoff_created", "client_intake", str(intake.id),
            reason="project_ready from confirmed positioning",
            metadata={"project_id": project["id"], "intake_id": str(intake.id)},
            commit=False,
        )
        await self._audit(
            db, user, "project_created_from_positioning", "geo_project", project["id"],
            reason="explicit project trigger after positioning confirmation",
            metadata={"intake_id": str(intake.id), "positioning_version": meta.get("positioning_version")},
            commit=False,
        )
        await db.commit()
        await db.refresh(intake)
        return project

    async def _find_positioning_project(self, db, intake, project_code=None):
        q = select(GeoProject).where(GeoProject.realm_id == intake.realm_id)
        if project_code:
            q = q.where(GeoProject.project_code == project_code)
        else:
            q = q.where(GeoProject.metadata_json["intake_id"].as_string() == str(intake.id))
        return (await db.execute(q.limit(1))).scalars().first()

    @staticmethod
    def _verify_positioning_project(project, intake):
        meta = project.metadata_json or {}
        if (
            str(project.realm_id) != str(intake.realm_id)
            or str(meta.get("intake_id") or "") != str(intake.id)
        ):
            raise ValueError("existing positioning project does not match realm or intake")

    async def _repair_or_reject_existing(
        self, db, user, intake, project, expected_position_version: int = None
    ) -> Dict:
        self._verify_positioning_project(project, intake)
        meta = intake.metadata_json or {}
        if (
            meta.get("flow_status") == "project_created"
            and meta.get("project_id") == str(project.id)
        ):
            if expected_position_version is not None and meta.get("positioning_version") != expected_position_version:
                raise ValueError("定位版本已变化，请刷新后重试")
            await db.commit()
            return self._project_dict(project)
        if meta.get("flow_status") not in ("positioning_confirmed", "project_created"):
            raise IntakeStateTransitionError(
                f"invalid_state_transition: {meta.get('flow_status', 'unknown')} -> project_created"
            )
        if meta.get("positioning_status") != "confirmed":
            raise ValueError("定位尚未确认")
        if expected_position_version is not None and meta.get("positioning_version") != expected_position_version:
            raise ValueError("定位版本已变化，请刷新后重试")
        intake.metadata_json = {
            **(meta or {}),
            "flow_status": "project_created",
            "project_id": str(project.id),
        }
        await self._audit(
            db, user, "project_handoff_repaired", "client_intake", str(intake.id),
            reason="existing project matched realm and intake",
            metadata={"project_id": str(project.id), "intake_id": str(intake.id)},
            commit=False,
        )
        await db.commit()
        await db.refresh(intake)
        return self._project_dict(project)

    async def _resolve_existing_after_conflict(
        self, db, user, intake_id: str, project_code: str, expected_position_version: int = None
    ) -> Dict:
        try:
            intake_uuid = uuid.UUID(str(intake_id))
        except (ValueError, TypeError):
            raise ValueError("intake_id must be a valid UUID")
        intake = (await db.execute(
            select(ClientIntake)
            .where(ClientIntake.id == intake_uuid)
            .with_for_update()
        )).scalars().first()
        if not intake:
            raise ValueError("intake not found")
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        await db.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
            {"key": f"positioning_project:{intake.id}"},
        )
        project = await self._find_positioning_project(db, intake, project_code=project_code)
        if not project:
            raise ValueError("positioning project conflict without matching project")
        self._verify_positioning_project(project, intake)
        meta = intake.metadata_json or {}
        if meta.get("flow_status") not in ("positioning_confirmed", "project_created"):
            raise IntakeStateTransitionError(
                f"invalid_state_transition: {meta.get('flow_status', 'unknown')} -> project_created"
            )
        if meta.get("positioning_status") != "confirmed":
            raise ValueError("定位尚未确认")
        if expected_position_version is not None and meta.get("positioning_version") != expected_position_version:
            raise ValueError("定位版本已变化，请刷新后重试")
        intake.metadata_json = {
            **(meta or {}),
            "flow_status": "project_created",
            "project_id": str(project.id),
        }
        await self._audit(
            db, user, "project_handoff_recovered", "client_intake", str(intake.id),
            reason="project recovered after concurrent creation conflict",
            metadata={"project_id": str(project.id), "intake_id": str(intake.id)},
            commit=False,
        )
        await db.commit()
        await db.refresh(intake)
        return self._project_dict(project)

    async def list_projects(self, db: AsyncSession, user, realm_id: str = None) -> List[Dict]:
        if realm_id and not await self._control(db, user, realm_id):
            raise PermissionError("realm owner/editor permission required")
        q = select(GeoProject).order_by(GeoProject.created_at.desc())
        if realm_id:
            registry = await self.realm_service.resolve_registry(db, realm_id)
            if not registry:
                raise ValueError('realm not found')
            q = q.where(GeoProject.realm_id == registry.id)
        rows = (await db.execute(q)).scalars().all()
        return [self._project_dict(p) for p in rows]

    async def get_project(self, db: AsyncSession, user, project_id: str) -> Dict:
        try:
            project = await db.get(GeoProject, uuid.UUID(str(project_id)))
        except (ValueError, TypeError):
            raise ValueError("project_id must be a valid UUID")
        if not project:
            raise ValueError("project not found")
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        return self._project_dict(project)

    async def create_work_item(self, db: AsyncSession, user, project_id: str, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        title = (data.get("title") or "").strip()
        work_type = (data.get("work_type") or "").strip()
        if not title or not work_type:
            raise ValueError("title and work_type are required")
        item = ProjectWorkItem(
            project_id=project.id,
            work_type=work_type,
            title=title,
            description=data.get("description"),
            status=data.get("status", "planned"),
            operator_id=user.id,
            input_manifest=data.get("input_manifest"),
            output_manifest=data.get("output_manifest"),
            source_fact_ids=data.get("source_fact_ids") or [],
            truth_status=(data.get("truth_status") if data.get("truth_status") in ("observed", "synthetic") else "observed"),
            may_affect_real_metrics=False,
            metadata_json=data.get("metadata"),
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        await self._audit(db, user, "project_work_item_created", "project_work_item", str(item.id),
                          reason=work_type)
        return self._work_item_dict(item)

    async def create_artifact(self, db: AsyncSession, user, project_id: str, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        title = (data.get("title") or "").strip()
        artifact_type = (data.get("artifact_type") or "").strip()
        if not title or not artifact_type:
            raise ValueError("title and artifact_type are required")
        artifact = ProjectArtifact(
            project_id=project.id,
            work_item_id=uuid.UUID(str(data["work_item_id"])) if data.get("work_item_id") else None,
            artifact_type=artifact_type,
            title=title,
            description=data.get("description"),
            content_json=data.get("content_json"),
            content_text=data.get("content_text"),
            citations=data.get("citations") or [],
            status=data.get("status", "draft"),
            operator_id=user.id,
            authorization_scope=data.get("authorization_scope"),
            source_fact_ids=data.get("source_fact_ids") or [],
            truth_status=(data.get("truth_status") if data.get("truth_status") in ("observed", "synthetic") else "observed"),
            may_affect_real_metrics=False,
            metadata_json=data.get("metadata"),
        )
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)
        await self._audit(db, user, "project_artifact_created", "project_artifact", str(artifact.id),
                          reason=artifact_type)
        return self._artifact_dict(artifact)

    async def create_tool_execution(self, db: AsyncSession, user, project_id: str, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        provider = (data.get("provider") or "").strip()
        tool_name = (data.get("tool_name") or "").strip()
        authorization_id = (data.get("authorization_id") or "").strip()
        if not provider or not tool_name:
            raise ValueError("provider and tool_name are required")
        if not authorization_id:
            raise ValueError("authorization_id is required for tool execution")
        check = await self.realm_service.validate_authorization(
            db, authorization_id,
            entity_id=str(project.realm_entity_id) if project.realm_entity_id else None,
            provider=provider,
            tool_name=tool_name,
            use_scope="ai_tools" if provider != "universe" else None,
        )
        if not check["valid"]:
            raise ValueError("; ".join(check["reasons"]))
        input_manifest = self._redact_manifest(data.get("input_manifest") or {})
        output_manifest = self._redact_manifest(data.get("output_manifest") or {})
        input_hash = hashlib.sha256(
            json.dumps(input_manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:32]
        output_hash = hashlib.sha256(
            json.dumps(output_manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:32]
        execution_source = "declared"
        record = ToolExecutionRecord(
            execution_code=f"EXEC-{uuid.uuid4().hex[:12].upper()}",
            project_id=project.id,
            realm_id=project.realm_id,
            realm_entity_id=project.realm_entity_id,
            authorization_id=uuid.UUID(authorization_id),
            authorization_hash=check["authorization_hash"],
            work_item_id=uuid.UUID(str(data["work_item_id"])) if data.get("work_item_id") else None,
            operator_id=user.id,
            provider=provider,
            tool_name=tool_name,
            model_name=data.get("model_name"),
            model_version=data.get("model_version"),
            input_manifest=input_manifest,
            output_manifest=output_manifest,
            input_manifest_hash=input_hash,
            output_manifest_hash=output_hash,
            source_fact_ids=data.get("source_fact_ids") or [],
            truth_status="observed",
            execution_source=execution_source,
            cost=float(data["cost"]) if data.get("cost") is not None else None,
            started_at=self._parse_dt(data.get("started_at")) or datetime.now(timezone.utc),
            completed_at=self._parse_dt(data.get("completed_at")),
            execution_status="declared",
            config_version=self.config.get("version", "1.0.0"),
            config_hash=self.config.get("config_hash"),
            citations=data.get("citations") or [],
            metadata_json=data.get("metadata"),
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        await self._audit(db, user, "tool_execution_recorded", "tool_execution_record", str(record.id),
                          reason=f"{provider}:{tool_name}")
        if data.get("work_item_id"):
            try:
                item = await db.get(ProjectWorkItem, uuid.UUID(str(data["work_item_id"])))
                if item and item.status not in ("completed", "archived"):
                    item.status = "in_progress"
                    item.last_synced_source = "tool_execution"
                    item.last_synced_at = datetime.now(timezone.utc)
                    await db.commit()
                    await self._audit(db, user, "work_item_synced_auto", "project_work_item", str(item.id), reason="tool_execution_recorded")
            except Exception:
                pass
        return self._tool_execution_dict(record)

    async def run_local_tool(self, db: AsyncSession, user, project_id: str, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        gov = get_governance_service()
        if not gov.is_reviewer(user):
            raise PermissionError("reviewer/admin permission required for system execution")
        authorization_id = (data.get("authorization_id") or "").strip()
        if not authorization_id:
            raise ValueError("authorization_id is required for tool execution")
        tool_name = (data.get("tool_name") or "geo_visibility").strip()
        check = await self.realm_service.validate_authorization(
            db, authorization_id,
            entity_id=str(project.realm_entity_id) if project.realm_entity_id else None,
            provider="universe",
            tool_name=tool_name,
        )
        if not check["valid"]:
            raise ValueError("; ".join(check["reasons"]))
        input_manifest = self._redact_manifest(data.get("input_manifest") or {
            "target_brand": project.target_brand,
            "question_set": project.question_set or [],
        })
        result = await run_local_tool(
            db, tool_name, input_manifest,
            str(project.realm_entity_id) if project.realm_entity_id else "",
        )
        output_manifest = self._redact_manifest(result.get("output_manifest") or {})
        input_hash = hashlib.sha256(
            json.dumps(input_manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:32]
        output_hash = hashlib.sha256(
            json.dumps(output_manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:32]
        record = ToolExecutionRecord(
            execution_code=f"EXEC-{uuid.uuid4().hex[:12].upper()}",
            project_id=project.id,
            realm_id=project.realm_id,
            realm_entity_id=project.realm_entity_id,
            authorization_id=uuid.UUID(authorization_id),
            authorization_hash=check["authorization_hash"],
            operator_id=user.id,
            provider="universe",
            tool_name=tool_name,
            model_name="local-rule",
            model_version="1.0.0",
            input_manifest=input_manifest,
            output_manifest=output_manifest,
            input_manifest_hash=input_hash,
            output_manifest_hash=output_hash,
            source_fact_ids=result.get("source_fact_ids") or [],
            truth_status="observed",
            execution_source="system",
            cost=float(result.get("cost") or 0),
            started_at=datetime.now(timezone.utc),
            completed_at=result.get("completed_at"),
            execution_status="success",
            config_version=self.config.get("version", "1.0.0"),
            config_hash=self.config.get("config_hash"),
            citations=[],
            metadata_json={"local_adapter": True, "tool": tool_name},
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        await self._audit(db, user, "tool_execution_system_recorded", "tool_execution_record", str(record.id),
                          reason=f"local real tool {tool_name}")
        return self._tool_execution_dict(record)

    async def create_outcome(self, db: AsyncSession, user, project_id: str, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        claim_text = (data.get("claim_text") or "").strip()
        outcome_type = (data.get("outcome_type") or "").strip()
        if not claim_text or not outcome_type:
            raise ValueError("claim_text and outcome_type are required")
        claim = None
        if data.get("evidence_claim_id"):
            try:
                claim = await db.get(EvidenceClaim, uuid.UUID(str(data["evidence_claim_id"])))
            except (ValueError, TypeError):
                raise ValueError("evidence_claim_id must be a valid UUID")
            if not claim:
                raise ValueError("evidence claim not found")
        status = "pending"
        truth = "observed"
        validation_reasons = []
        rule_version = None
        config_version = None
        config_hash = None
        if claim:
            validation = await self._validate_outcome_claim(db, project, claim, outcome_type, claim_text)
            if not validation["valid"] and claim.truth_status == "verified":
                raise ValueError("; ".join(validation["reasons"]))
            status = validation["status"]
            truth = validation["truth_status"]
            validation_reasons = validation["reasons"]
            rule_version = self.config.get("version", "1.1.0")
            config_version = self.config.get("version", "1.1.0")
            config_hash = self.config.get("config_hash")
        outcome = ProjectOutcome(
            outcome_code=f"OUT-{uuid.uuid4().hex[:12].upper()}",
            project_id=project.id,
            outcome_type=outcome_type,
            claim_text=claim_text,
            status=status,
            evidence_claim_id=claim.id if claim else None,
            truth_status=truth,
            validation_rule_version=rule_version,
            validation_config_version=config_version,
            validation_config_hash=config_hash,
            validation_reasons=validation_reasons,
            operator_id=user.id,
            metadata_json=data.get("metadata"),
        )
        db.add(outcome)
        await db.commit()
        await db.refresh(outcome)
        await self._audit(db, user, "project_outcome_recorded", "project_outcome", str(outcome.id),
                          reason=status)
        return self._outcome_dict(outcome)

    async def refresh_outcome(self, db: AsyncSession, user, outcome_id: str) -> Dict:
        try:
            outcome = await db.get(ProjectOutcome, uuid.UUID(str(outcome_id)))
        except (ValueError, TypeError):
            raise ValueError("outcome_id must be a valid UUID")
        if not outcome:
            raise ValueError("outcome not found")
        project = await self._require_project(db, str(outcome.project_id))
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        if outcome.evidence_claim_id:
            claim = await db.get(EvidenceClaim, outcome.evidence_claim_id)
            if not claim or claim.truth_status != "verified":
                outcome.status = "revoked"
                outcome.truth_status = "observed"
                outcome.revoked_at = datetime.now(timezone.utc)
                outcome.revoked_by = user.id
                outcome.revocation_reason = "source claim no longer verified"
                outcome.validation_reasons = (outcome.validation_reasons or []) + ["source_claim_revoked"]
                await db.commit()
                await db.refresh(outcome)
        return self._outcome_dict(outcome)

    async def timeline(self, db: AsyncSession, user, project_id: str) -> List[Dict]:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        work = (await db.execute(select(ProjectWorkItem).where(ProjectWorkItem.project_id == project.id))).scalars().all()
        arts = (await db.execute(select(ProjectArtifact).where(ProjectArtifact.project_id == project.id))).scalars().all()
        runs = (await db.execute(select(ToolExecutionRecord).where(ToolExecutionRecord.project_id == project.id))).scalars().all()
        outcomes = (await db.execute(select(ProjectOutcome).where(ProjectOutcome.project_id == project.id))).scalars().all()
        items = []
        for w in work:
            items.append({"type": "work_item", "label": w.title, "at": w.created_at.isoformat(), "status": w.status, "truth_status": w.truth_status})
        for a in arts:
            items.append({"type": "artifact", "label": a.title, "at": a.created_at.isoformat(), "status": a.status, "truth_status": a.truth_status})
        for r in runs:
            items.append({"type": "tool_execution", "label": f"{r.provider}:{r.tool_name}", "at": (r.completed_at or r.started_at or r.created_at).isoformat(), "status": r.execution_status, "truth_status": r.truth_status})
        for o in outcomes:
            items.append({"type": "outcome", "label": o.claim_text, "at": o.created_at.isoformat(), "status": o.status, "truth_status": o.truth_status})
        items.sort(key=lambda x: x.get("at") or "", reverse=True)
        return items

    async def project_assets(self, db: AsyncSession, user, project_id: str) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        arts = (await db.execute(select(ProjectArtifact).where(ProjectArtifact.project_id == project.id))).scalars().all()
        assets = (await db.execute(
            select(RealmDataAsset).where(RealmDataAsset.project_id == project.id)
        )).scalars().all()
        return {
            "artifacts": [self._artifact_dict(a) for a in arts],
            "realm_data_assets": [self._asset_dict(a) for a in assets],
        }

    async def publish_artifact(self, db: AsyncSession, user, artifact_id: str, data: Dict) -> Dict:
        try:
            artifact = await db.get(ProjectArtifact, uuid.UUID(str(artifact_id)))
        except (ValueError, TypeError):
            raise ValueError("artifact_id must be a valid UUID")
        if not artifact:
            raise ValueError("artifact not found")
        project = await self._require_project(db, str(artifact.project_id))
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        if artifact.status == "archived":
            raise ValueError("archived artifact cannot be published")
        self._validate_external_url(data.get("published_url"), "published_url")
        content = artifact.content_text or ""
        content_hash = hashlib.sha256(
            (content + json.dumps(artifact.content_json or {}, sort_keys=True, ensure_ascii=False)).encode("utf-8")
        ).hexdigest()[:32]
        artifact.status = "published"
        artifact.published_url = data.get("published_url")
        artifact.published_at = datetime.now(timezone.utc)
        artifact.published_by = user.id
        artifact.content_hash = content_hash
        artifact.delivery_recipient = data.get("delivery_recipient")
        artifact.metadata_json = {**(artifact.metadata_json or {}), "delivery_note": data.get("note")}
        await db.commit()
        await db.refresh(artifact)
        await self._audit(db, user, "project_artifact_published", "project_artifact", str(artifact.id),
                          reason="manual publish/delivery")
        return self._artifact_dict(artifact)

    async def record_monitoring_result(self, db: AsyncSession, user, project_id: str, data: Dict) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        metric_key = (data.get("metric_key") or "").strip()
        if not metric_key:
            raise ValueError("metric_key is required")
        self._validate_external_url(data.get("raw_result_ref"), "raw_result_ref")
        observed_at = self._parse_dt(data.get("observed_at")) or datetime.now(timezone.utc)
        outcome = ProjectOutcome(
            outcome_code=f"OUT-{uuid.uuid4().hex[:12].upper()}",
            project_id=project.id,
            outcome_type="monitoring_result",
            claim_text=data.get("claim_text") or f"monitoring {metric_key}",
            status="observed",
            truth_status="observed",
            observed_at=observed_at,
            raw_result_ref=data.get("raw_result_ref"),
            metric_key=metric_key,
            metric_value=float(data["metric_value"]) if data.get("metric_value") is not None else None,
            operator_id=user.id,
            metadata_json={"monitoring": True, "source": data.get("source", "manual")},
        )
        db.add(outcome)
        await db.commit()
        await db.refresh(outcome)
        await self._audit(db, user, "project_monitoring_recorded", "project_outcome", str(outcome.id),
                          reason=metric_key)
        return self._outcome_dict(outcome)

    async def project_summary(self, db: AsyncSession, user, project_id: str) -> Dict:
        project = await self._require_project(db, project_id)
        if not await self._control(db, user, str(project.realm_id)):
            raise PermissionError("realm owner/editor permission required")
        artifacts = (await db.execute(
            select(ProjectArtifact).where(ProjectArtifact.project_id == project.id)
        )).scalars().all()
        runs = (await db.execute(
            select(ToolExecutionRecord).where(ToolExecutionRecord.project_id == project.id)
        )).scalars().all()
        outcomes = (await db.execute(
            select(ProjectOutcome).where(ProjectOutcome.project_id == project.id)
        )).scalars().all()
        cost = sum(r.cost or 0 for r in runs)
        times = [r.started_at for r in runs if r.started_at] + [r.completed_at for r in runs if r.completed_at]
        duration_days = None
        if times:
            duration_days = round((max(times) - min(times)).total_seconds() / 86400.0, 2)
        return {
            "project_id": str(project.id),
            "name": project.name,
            "status": project.status,
            "artifacts": {
                "total": len(artifacts),
                "published": sum(1 for a in artifacts if a.status == "published"),
                "draft": sum(1 for a in artifacts if a.status == "draft"),
                "archived": sum(1 for a in artifacts if a.status == "archived"),
            },
            "tool_executions": {
                "total": len(runs),
                "declared": sum(1 for r in runs if r.execution_source == "declared"),
                "system": sum(1 for r in runs if r.execution_source == "system"),
                "success": sum(1 for r in runs if r.execution_status == "success"),
                "failed": sum(1 for r in runs if r.execution_status == "failed"),
                "cost": round(cost, 4),
            },
            "outcomes": {
                "total": len(outcomes),
                "by_status": {s: sum(1 for o in outcomes if o.status == s) for s in {
                    "pending", "claimed", "observed", "verified", "rejected", "revoked"
                }},
            },
            "duration_days": duration_days,
            "monitoring_results": sum(1 for o in outcomes if o.outcome_type == "monitoring_result"),
        }

    async def list_draft_artifacts(self, db: AsyncSession, user) -> List[Dict]:
        gov = get_governance_service()
        if not gov.is_reviewer(user):
            raise PermissionError("reviewer/admin permission required")
        rows = (await db.execute(
            select(ProjectArtifact).where(ProjectArtifact.status == "draft")
            .order_by(ProjectArtifact.created_at.desc()).limit(200)
        )).scalars().all()
        return [self._artifact_dict(a) for a in rows]

    async def _validate_outcome_claim(self, db, project: GeoProject, claim: EvidenceClaim,
                                      outcome_type: str, claim_text: str) -> Dict:
        if claim.truth_status != "verified":
            return {
                "valid": False,
                "status": "claimed",
                "truth_status": "observed",
                "reasons": ["claim_not_verified"],
            }
        reasons = []
        now = datetime.now(timezone.utc)
        evidence = await db.get(Evidence, claim.evidence_id)
        if not evidence:
            reasons.append("evidence_not_found")
        else:
            if evidence.truth_status != "verified":
                reasons.append("evidence_not_verified")
            if not evidence.may_affect_real_metrics:
                reasons.append("evidence_may_affect_real_metrics_false")
            if evidence.expires_at and evidence.expires_at < now:
                reasons.append("evidence_expired")
        if not claim.may_affect_real_metrics:
            reasons.append("claim_may_affect_real_metrics_false")
        if claim.valid_until and claim.valid_until < now:
            reasons.append("claim_expired")
        if str(claim.subject_id) != str(project.realm_entity_id):
            reasons.append("claim_subject_realm_mismatch")

        outcome_rules = self.config.get("outcome", {}).get("predicates", {}).get(outcome_type, {})
        allowed_predicates = set(outcome_rules.get("allowed_predicates", []))
        allowed_objects = set(outcome_rules.get("allowed_objects", []))
        if claim.predicate_code not in allowed_predicates:
            reasons.append(f"predicate_not_allowed_for_{outcome_type}")
        if claim.object_code not in allowed_objects:
            reasons.append(f"object_not_allowed_for_{outcome_type}")
        if claim.object_value:
            text_a = claim_text or ""
            text_b = str(claim.object_value)
            if not (text_a.lower() in text_b.lower() or text_b.lower() in text_a.lower()):
                reasons.append("object_value_mismatch")
        else:
            reasons.append("object_value_required")

        metadata = claim.metadata_json or {}
        chain_ok = str(metadata.get("project_id") or "") == str(project.id)
        if metadata.get("artifact_id"):
            artifact = await db.get(ProjectArtifact, uuid.UUID(str(metadata["artifact_id"])))
            if artifact and str(artifact.project_id) == str(project.id):
                chain_ok = True
        if not chain_ok:
            reasons.append("missing_project_source_chain")

        valid = not reasons
        return {
            "valid": valid,
            "status": "verified" if valid else "pending",
            "truth_status": "verified" if valid else "observed",
            "reasons": reasons,
        }

    @staticmethod
    def _redact_manifest(manifest: Dict) -> Dict:
        sensitive_keys = ("secret", "password", "token", "api_key", "authorization", "private_key")
        redacted = {}
        for key, value in (manifest or {}).items():
            lowered = str(key).lower()
            if any(s in lowered for s in sensitive_keys) and value is not None:
                redacted[key] = "[redacted]"
            elif isinstance(value, dict):
                redacted[key] = GeoProjectService._redact_manifest(value)
            elif isinstance(value, list):
                redacted[key] = [
                    GeoProjectService._redact_manifest(v) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                redacted[key] = value
        return redacted

    @staticmethod
    def _validate_external_url(value, field: str):
        if not value or not str(value).strip():
            return
        url = str(value).strip()
        try:
            normalized = validate_url(url)
            resolve_all_and_validate(urlparse(normalized).hostname)
        except ValueError as e:
            raise ValueError(f"{field} failed C6.3 safety validation: {e}")

    async def _require_project(self, db, project_id: str) -> GeoProject:
        try:
            project = await db.get(GeoProject, uuid.UUID(str(project_id)))
        except (ValueError, TypeError):
            raise ValueError("project_id must be a valid UUID")
        if not project:
            raise ValueError("project not found")
        return project

    def _project_dict(self, p: GeoProject) -> Dict:
        return {
            "id": str(p.id),
            "project_code": p.project_code,
            "realm_id": str(p.realm_id),
            "realm_entity_id": str(p.realm_entity_id) if p.realm_entity_id else None,
            "name": p.name,
            "objective": p.objective,
            "target_brand": p.target_brand,
            "target_product": p.target_product,
            "target_audience": p.target_audience,
            "scenario": p.scenario,
            "problems": p.problems or [],
            "ai_platforms": p.ai_platforms or [],
            "question_set": p.question_set or [],
            "competitors": p.competitors or [],
            "expected_outcome": p.expected_outcome,
            "lifecycle_state": p.lifecycle_state,
            "status": p.status,
            "truth_status": p.truth_status,
            "may_affect_real_metrics": p.may_affect_real_metrics,
            "metadata_json": p.metadata_json or {},
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }

    def _work_item_dict(self, w: ProjectWorkItem) -> Dict:
        return {
            "phase": w.phase,
            "purpose": w.purpose,
            "reason": w.reason,
            "owner_id": str(w.owner_id) if w.owner_id else None,
            "owner_label": (w.metadata_json or {}).get("owner_label"),
            "start_at": w.start_at.isoformat() if w.start_at else None,
            "due_at": w.due_at.isoformat() if w.due_at else None,
            "depends_on": w.depends_on or [],
            "acceptance_criteria": w.acceptance_criteria,
            "required_materials": w.required_materials or [],
            "evidence_ids": w.evidence_ids or [],
            "risks": w.risks or [],
            "reminder_at": w.reminder_at.isoformat() if w.reminder_at else None,
            "execution_mode": w.execution_mode,
            "progress": w.progress,
            "completion_note": w.completion_note,
            "last_synced_source": w.last_synced_source,
            "last_synced_at": w.last_synced_at.isoformat() if w.last_synced_at else None,
            "id": str(w.id),
            "project_id": str(w.project_id),
            "work_type": w.work_type,
            "title": w.title,
            "description": w.description,
            "status": w.status,
            "input_manifest": w.input_manifest,
            "output_manifest": w.output_manifest,
            "source_fact_ids": w.source_fact_ids or [],
            "truth_status": w.truth_status,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }

    def _artifact_dict(self, a: ProjectArtifact) -> Dict:
        return {
            "id": str(a.id),
            "project_id": str(a.project_id),
            "work_item_id": str(a.work_item_id) if a.work_item_id else None,
            "artifact_type": a.artifact_type,
            "title": a.title,
            "description": a.description,
            "content_json": a.content_json,
            "content_text": a.content_text,
            "citations": a.citations or [],
            "status": a.status,
            "published_url": a.published_url,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "published_by": str(a.published_by) if a.published_by else None,
            "content_hash": a.content_hash,
            "delivery_recipient": a.delivery_recipient,
            "authorization_scope": a.authorization_scope,
            "source_fact_ids": a.source_fact_ids or [],
            "truth_status": a.truth_status,
            "may_affect_real_metrics": a.may_affect_real_metrics,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }

    def _tool_execution_dict(self, r: ToolExecutionRecord) -> Dict:
        return {
            "id": str(r.id),
            "execution_code": r.execution_code,
            "project_id": str(r.project_id) if r.project_id else None,
            "realm_id": str(r.realm_id) if r.realm_id else None,
            "realm_entity_id": str(r.realm_entity_id) if r.realm_entity_id else None,
            "authorization_id": str(r.authorization_id) if r.authorization_id else None,
            "authorization_hash": r.authorization_hash,
            "work_item_id": str(r.work_item_id) if r.work_item_id else None,
            "provider": r.provider,
            "tool_name": r.tool_name,
            "capability_id": r.capability_id,
            "capability_version": r.capability_version,
            "capability_type": r.capability_type,
            "source_mode": r.source_mode,
            "model_name": r.model_name,
            "model_version": r.model_version,
            "input_manifest": r.input_manifest,
            "output_manifest": r.output_manifest,
            "input_manifest_hash": r.input_manifest_hash,
            "output_manifest_hash": r.output_manifest_hash,
            "source_fact_ids": r.source_fact_ids or [],
            "truth_status": r.truth_status,
            "execution_source": r.execution_source,
            "cost": r.cost,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "execution_status": r.execution_status,
            "config_version": r.config_version,
            "config_hash": r.config_hash,
            "citations": r.citations or [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }

    def _outcome_dict(self, o: ProjectOutcome) -> Dict:
        return {
            "id": str(o.id),
            "outcome_code": o.outcome_code,
            "project_id": str(o.project_id),
            "outcome_type": o.outcome_type,
            "claim_text": o.claim_text,
            "status": o.status,
            "evidence_claim_id": str(o.evidence_claim_id) if o.evidence_claim_id else None,
            "truth_status": o.truth_status,
            "validation_rule_version": o.validation_rule_version,
            "validation_config_version": o.validation_config_version,
            "validation_config_hash": o.validation_config_hash,
            "validation_reasons": o.validation_reasons or [],
            "observed_at": o.observed_at.isoformat() if o.observed_at else None,
            "raw_result_ref": o.raw_result_ref,
            "metric_key": o.metric_key,
            "metric_value": o.metric_value,
            "revoked_at": o.revoked_at.isoformat() if o.revoked_at else None,
            "revoked_by": str(o.revoked_by) if o.revoked_by else None,
            "revocation_reason": o.revocation_reason,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }

    def _asset_dict(self, a: RealmDataAsset) -> Dict:
        return {
            "id": str(a.id),
            "asset_key": a.asset_key,
            "asset_type": a.asset_type,
            "title": a.title,
            "truth_status": a.truth_status,
            "may_affect_real_metrics": a.may_affect_real_metrics,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }

    @staticmethod
    def _parse_dt(value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None


def get_geo_project_service() -> GeoProjectService:
    return GeoProjectService()
