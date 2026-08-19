"""V10.1 Sixth Business Module service.

Unified capability registry and run/trace for three source modes:
platform_standard, realm_owner, external_connected.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capability_definition import CapabilityDefinition
from app.models.geo_project import GeoProject, ToolExecutionRecord
from app.services.governance import get_governance_service
from app.services.realm_service import get_realm_service
from app.services.local_tool_adapter import run_local_tool


def _load_capability_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "config", "universe", "capabilities.yaml",
    )
    if os.path.exists(p):
        raw = open(p, encoding="utf-8").read()
        data = yaml.safe_load(raw) or {}
        data["config_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return data
    return {"version": "1.0.0", "config_hash": "missing", "platform_standard": [], "external_connected": []}


class CapabilityService:
    def __init__(self):
        self.config = _load_capability_config()
        self.realm_service = get_realm_service()

    async def _control(self, db: AsyncSession, user, realm_entity_id: str) -> bool:
        return await self.realm_service._control(db, user, realm_entity_id)

    async def _audit(self, db, user, action, target_type, target_id, reason=None, metadata=None):
        await get_governance_service().audit(
            db, user.id, action, target_type, target_id,
            reason=reason, actor_label=user.name, metadata=metadata
        )

    async def list(self, db: AsyncSession, user, source_mode: str = None,
                   capability_type: str = None, realm_entity_id: str = None) -> List[Dict]:
        if realm_entity_id and not await self._control(db, user, realm_entity_id):
            raise PermissionError("realm owner/editor permission required")
        result = []
        catalog = []
        if source_mode in (None, "platform_standard"):
            catalog.extend(self.config.get("platform_standard", []))
        if source_mode in (None, "external_connected"):
            catalog.extend(self.config.get("external_connected", []))
        for item in catalog:
            if capability_type and item.get("capability_type") != capability_type:
                continue
            cap = self._from_config(item)
            if cap["source_mode"] == "external_connected" and cap["status"] == "configured_false":
                cap["available"] = False
                cap["reason"] = "provider not configured"
            result.append(cap)

        db_query = select(CapabilityDefinition)
        if source_mode:
            db_query = db_query.where(CapabilityDefinition.source_mode == source_mode)
        if capability_type:
            db_query = db_query.where(CapabilityDefinition.capability_type == capability_type)
        if realm_entity_id:
            db_query = db_query.where(
                (CapabilityDefinition.realm_entity_id == uuid.UUID(str(realm_entity_id)))
                | (CapabilityDefinition.owner_id == user.id)
            )
        rows = (await db.execute(db_query.order_by(CapabilityDefinition.created_at.desc()))).scalars().all()
        for row in rows:
            cap = self._to_dict(row)
            if row.status in ("draft", "private") and str(row.owner_id) != str(user.id):
                if not realm_entity_id or not await self._control(db, user, realm_entity_id):
                    continue
            result.append(cap)
        return result

    def list_public(self) -> List[Dict]:
        result = []
        for item in self.config.get("platform_standard", []):
            cap = self._from_config(item)
            result.append(cap)
        return result

    async def create(self, db: AsyncSession, user, data: Dict) -> Dict:
        realm_entity_id = data.get("realm_entity_id")
        name = (data.get("name") or "").strip()
        capability_type = (data.get("capability_type") or "").strip()
        source_mode = (data.get("source_mode") or "realm_owner").strip()
        if not realm_entity_id or not name or not capability_type:
            raise ValueError("realm_entity_id, name and capability_type are required")
        if source_mode != "realm_owner":
            raise ValueError("domain owner can only create realm_owner capabilities")
        if capability_type not in set(self.config.get("capability_types", [])):
            raise ValueError("invalid capability_type")
        if not await self._control(db, user, realm_entity_id):
            raise PermissionError("realm owner/editor permission required")
        provider = data.get("provider") or "realm_owner"
        tool_name = data.get("tool_name") or capability_type
        payload = {
            "name": name,
            "capability_type": capability_type,
            "source_mode": source_mode,
            "provider": provider,
            "tool_name": tool_name,
            "realm_entity_id": str(realm_entity_id),
        }
        config_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:32]
        cap = CapabilityDefinition(
            capability_id=f"cap-{uuid.uuid4().hex[:12]}",
            name=name,
            capability_type=capability_type,
            source_mode=source_mode,
            status=data.get("status", "draft"),
            publisher=data.get("publisher") or user.name,
            owner_id=user.id,
            realm_entity_id=uuid.UUID(str(realm_entity_id)),
            provider=provider,
            tool_name=tool_name,
            model_name=data.get("model_name"),
            model_version=data.get("model_version"),
            description=data.get("description"),
            input_schema=data.get("input_schema"),
            output_schema=data.get("output_schema"),
            required_authorization_scope=data.get("required_authorization_scope", "project_evidence"),
            allow_external_processing=bool(data.get("allow_external_processing", False)),
            data_destination=data.get("data_destination"),
            config_version=self.config.get("version", "1.0.0"),
            config_hash=config_hash,
            metadata_json=data.get("metadata"),
        )
        db.add(cap)
        await db.commit()
        await db.refresh(cap)
        await self._audit(db, user, "capability_created", "capability_definition", str(cap.id),
                          reason=f"{source_mode}:{capability_type}")
        return self._to_dict(cap)

    async def get(self, db: AsyncSession, user, capability_id: str) -> Dict:
        for item in self.config.get("platform_standard", []) + self.config.get("external_connected", []):
            if item.get("capability_id") == capability_id:
                cap = self._from_config(item)
                if cap["source_mode"] == "external_connected" and cap["status"] == "configured_false":
                    cap["available"] = False
                    cap["reason"] = "provider not configured"
                return cap
        row = (await db.execute(
            select(CapabilityDefinition).where(CapabilityDefinition.capability_id == capability_id)
        )).scalars().first()
        if not row:
            raise ValueError("capability not found")
        if row.status in ("draft", "private") and str(row.owner_id) != str(user.id):
            if not await self._control(db, user, str(row.realm_entity_id)):
                raise PermissionError("capability is private")
        return self._to_dict(row)

    async def run(self, db: AsyncSession, user, capability_id: str, data: Dict) -> Dict:
        cap = await self.get(db, user, capability_id)
        project_id = data.get("project_id")
        authorization_id = (data.get("authorization_id") or "").strip()
        if not project_id or not authorization_id:
            raise ValueError("project_id and authorization_id are required")
        try:
            project = await db.get(GeoProject, uuid.UUID(str(project_id)))
        except (ValueError, TypeError):
            raise ValueError("project_id must be a valid UUID")
        if not project:
            raise ValueError("project not found")
        if not await self._control(db, user, str(project.realm_entity_id)):
            raise PermissionError("realm owner/editor permission required")

        provider = cap.get("provider") or "universe"
        tool_name = cap.get("tool_name") or "geo_visibility"
        required_scope = cap.get("required_authorization_scope")
        check = await self.realm_service.validate_authorization(
            db, authorization_id,
            entity_id=str(project.realm_entity_id) if project.realm_entity_id else None,
            provider=provider,
            tool_name=tool_name,
            use_scope=required_scope,
        )
        if not check["valid"]:
            raise ValueError("; ".join(check["reasons"]))

        input_manifest = self._redact(data.get("input_manifest") or {
            "target_brand": project.target_brand,
            "question_set": project.question_set or [],
        })
        output_manifest = self._redact(data.get("output_manifest") or {})
        execution_source = "declared"
        execution_status = "declared"
        truth_status = "observed"
        result = None
        source_mode = cap.get("source_mode", "platform_standard")
        if source_mode == "platform_standard" and tool_name in ("geo_visibility", "geo_diagnosis", "geo_report"):
            result = await run_local_tool(
                db, tool_name, input_manifest,
                str(project.realm_entity_id) if project.realm_entity_id else "",
            )
            output_manifest = self._redact(result.get("output_manifest") or {})
            execution_source = "system"
            execution_status = result.get("status", "success")
        elif source_mode == "realm_owner" and tool_name in ("geo_visibility", "geo_diagnosis", "geo_report"):
            result = await run_local_tool(
                db, tool_name, input_manifest,
                str(project.realm_entity_id) if project.realm_entity_id else "",
            )
            output_manifest = self._redact(result.get("output_manifest") or {})
            execution_source = "system"
            execution_status = result.get("status", "success")
        elif source_mode == "external_connected":
            if not data.get("output_manifest"):
                raise ValueError("external manual import requires output_manifest")
        # external_connected/realm_owner custom without local tool remain declared observed
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
            provider=provider,
            tool_name=tool_name,
            capability_id=capability_id,
            capability_version=cap.get("config_version") or cap.get("model_version") or "1.0.0",
            capability_type=cap.get("capability_type"),
            source_mode=source_mode,
            model_name=cap.get("model_name"),
            model_version=cap.get("model_version"),
            input_manifest=input_manifest,
            output_manifest=output_manifest,
            input_manifest_hash=input_hash,
            output_manifest_hash=output_hash,
            source_fact_ids=data.get("source_fact_ids") or (result or {}).get("source_fact_ids") or [],
            truth_status=truth_status,
            execution_source=execution_source,
            cost=float(data.get("cost", 0) or 0) if not result else float(result.get("cost") or 0),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc) if execution_source == "system" else None,
            execution_status=execution_status,
            config_version=cap.get("config_version") or self.config.get("version", "1.0.0"),
            config_hash=cap.get("config_hash") or self.config.get("config_hash"),
            citations=data.get("citations") or [],
            metadata_json={"capability_id": capability_id, "source_mode": source_mode},
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        await self._audit(db, user, "capability_run_recorded", "tool_execution_record", str(record.id),
                          reason=f"{source_mode}:{capability_id}")
        return self._run_dict(record)

    async def list_runs(self, db: AsyncSession, user, project_id: str = None,
                        realm_entity_id: str = None) -> List[Dict]:
        q = select(ToolExecutionRecord).order_by(ToolExecutionRecord.created_at.desc())
        if project_id:
            project = await db.get(GeoProject, uuid.UUID(str(project_id)))
            if not project:
                raise ValueError("project not found")
            if not await self._control(db, user, str(project.realm_entity_id)):
                raise PermissionError("realm owner/editor permission required")
            q = q.where(ToolExecutionRecord.project_id == project.id)
        if realm_entity_id:
            if not await self._control(db, user, realm_entity_id):
                raise PermissionError("realm owner/editor permission required")
            q = q.where(ToolExecutionRecord.realm_entity_id == uuid.UUID(str(realm_entity_id)))
        rows = (await db.execute(q.limit(200))).scalars().all()
        return [self._run_dict(r) for r in rows]

    async def get_run(self, db: AsyncSession, user, run_id: str) -> Dict:
        try:
            run = await db.get(ToolExecutionRecord, uuid.UUID(str(run_id)))
        except (ValueError, TypeError):
            raise ValueError("run_id must be a valid UUID")
        if not run:
            raise ValueError("run not found")
        if not await self._control(db, user, str(run.realm_entity_id)):
            raise PermissionError("realm owner/editor permission required")
        return self._run_dict(run)

    def _from_config(self, item: Dict) -> Dict:
        return {
            "capability_id": item.get("capability_id"),
            "name": item.get("name"),
            "capability_type": item.get("capability_type"),
            "source_mode": "platform_standard" if item in self.config.get("platform_standard", []) else "external_connected",
            "status": item.get("status", "active"),
            "publisher": "恒域世界平台",
            "provider": item.get("provider"),
            "tool_name": item.get("tool_name"),
            "model_name": item.get("model_name"),
            "model_version": item.get("model_version"),
            "description": item.get("description"),
            "required_authorization_scope": item.get("required_authorization_scope"),
            "allow_external_processing": bool(item.get("allow_external_processing", False)),
            "data_destination": item.get("data_destination"),
            "config_version": item.get("model_version") or self.config.get("version", "1.0.0"),
            "config_hash": self.config.get("config_hash"),
            "configured": bool(item.get("configured", True)),
            "available": bool(item.get("configured", True)),
        }

    def _to_dict(self, c: CapabilityDefinition) -> Dict:
        return {
            "capability_id": c.capability_id,
            "name": c.name,
            "capability_type": c.capability_type,
            "source_mode": c.source_mode,
            "status": c.status,
            "publisher": c.publisher,
            "owner_id": str(c.owner_id) if c.owner_id else None,
            "realm_entity_id": str(c.realm_entity_id) if c.realm_entity_id else None,
            "provider": c.provider,
            "tool_name": c.tool_name,
            "model_name": c.model_name,
            "model_version": c.model_version,
            "description": c.description,
            "required_authorization_scope": c.required_authorization_scope,
            "allow_external_processing": c.allow_external_processing,
            "data_destination": c.data_destination,
            "config_version": c.config_version,
            "config_hash": c.config_hash,
            "available": True,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }

    def _run_dict(self, r: ToolExecutionRecord) -> Dict:
        return {
            "id": str(r.id),
            "execution_code": r.execution_code,
            "project_id": str(r.project_id) if r.project_id else None,
            "realm_entity_id": str(r.realm_entity_id) if r.realm_entity_id else None,
            "authorization_id": str(r.authorization_id) if r.authorization_id else None,
            "authorization_hash": r.authorization_hash,
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
            "truth_status": r.truth_status,
            "execution_source": r.execution_source,
            "execution_status": r.execution_status,
            "cost": r.cost,
            "config_version": r.config_version,
            "config_hash": r.config_hash,
            "citations": r.citations or [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }

    @staticmethod
    def _redact(manifest: Dict) -> Dict:
        sensitive_keys = ("secret", "password", "token", "api_key", "authorization", "private_key")
        redacted = {}
        for key, value in (manifest or {}).items():
            lowered = str(key).lower()
            if any(s in lowered for s in sensitive_keys) and value is not None:
                redacted[key] = "[redacted]"
            elif isinstance(value, dict):
                redacted[key] = CapabilityService._redact(value)
            elif isinstance(value, list):
                redacted[key] = [CapabilityService._redact(v) if isinstance(v, dict) else v for v in value]
            else:
                redacted[key] = value
        return redacted


def get_capability_service() -> CapabilityService:
    return CapabilityService()
