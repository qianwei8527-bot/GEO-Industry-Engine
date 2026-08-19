"""Simulated end-to-end loop for infrastructure validation.

Every record created by this service is explicitly marked simulation and
must never affect real metrics, relationships, Reputation or verified state.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intake import ClientIntake, IntakeAnalysis
from app.models.realm import RealmRegistry
from app.services.execution_plan_service import get_execution_plan_service
from app.services.geo_project_service import get_geo_project_service
from app.services.governance import get_governance_service
from app.services.realm_service import get_realm_service

SIMULATION_SAMPLE_TEXT = (
    "品牌名称：恒域模拟品牌\n"
    "企业主体：模拟企业有限公司\n"
    "产品：GEO模拟服务\n"
    "问题：从零开始建立GEO认知与转化路径\n"
    "转化目标：让品牌在AI搜索中被真实客户看见\n"
)


def _simulation_fields() -> List[Dict]:
    return [
        {
            "key": "brand_name",
            "label": "品牌名称",
            "value": "恒域模拟品牌",
            "status": "observed",
            "confidence": 1.0,
            "source_file": None,
            "notes": "模拟闭环样本，非真实客户",
        },
        {
            "key": "enterprise_entity",
            "label": "企业主体",
            "value": "模拟企业有限公司",
            "status": "observed",
            "confidence": 1.0,
            "source_file": None,
            "notes": "模拟闭环样本，非真实客户",
        },
        {
            "key": "product_service",
            "label": "核心产品或服务",
            "value": "GEO模拟服务",
            "status": "observed",
            "confidence": 1.0,
            "source_file": None,
            "notes": "模拟闭环样本，非真实客户",
        },
        {
            "key": "client_problem",
            "label": "客户希望解决的问题",
            "value": "从零开始建立GEO认知与转化路径",
            "status": "observed",
            "confidence": 1.0,
            "source_file": None,
            "notes": "模拟闭环样本，非真实客户",
        },
        {
            "key": "industry_track",
            "label": "所属行业与细分赛道",
            "value": "待补充",
            "status": "unknown",
            "confidence": 0.0,
            "source_file": None,
            "notes": "模拟闭环故意保留未知项，验证 partial 状态",
        },
        {
            "key": "existing_channels",
            "label": "现有渠道",
            "value": "待补充",
            "status": "unknown",
            "confidence": 0.0,
            "source_file": None,
            "notes": "模拟闭环故意保留未知项",
        },
    ]


class SimulationLoopService:
    def __init__(self):
        self.realm_service = get_realm_service()
        self.geo_project_service = get_geo_project_service()
        self.execution_plan_service = get_execution_plan_service()
        self.gov = get_governance_service()

    async def _registry(self, db, realm_ref: str) -> Optional[RealmRegistry]:
        return await self.realm_service.resolve_registry(db, realm_ref)

    async def run(self, db: AsyncSession, user, realm_ref: str) -> Dict:
        registry = await self._registry(db, realm_ref)
        if not registry:
            raise ValueError("realm not found")
        if not await self.realm_service._control(db, user, str(registry.entity_id)):
            raise PermissionError("realm owner/editor permission required")

        intake = ClientIntake(
            intake_code=f"SIM-{uuid.uuid4().hex[:12].upper()}",
            realm_id=registry.id,
            realm_entity_id=registry.entity_id,
            status="owner_confirmed",
            relationship="模拟关系",
            pasted_text=SIMULATION_SAMPLE_TEXT,
            supplemental_notes="模拟闭环数据，仅用于基础设施验证",
            file_manifest=[],
            source_truth_status="simulation",
            created_by=user.id,
            confirmed_by=user.id,
            confirmed_at=datetime.now(timezone.utc),
            metadata_json={
                "simulation": True,
                "simulation_level": "demo",
                "simulation_source": "simulation_loop",
                "loop_version": "1.0.0",
            },
        )
        db.add(intake)
        await db.flush()
        await db.refresh(intake)

        fields = _simulation_fields()
        analysis = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=1,
            status="confirmed",
            analysis_json={
                "fields": fields,
                "summary": "模拟闭环：已提取可验证链路，同时保留 unknown 以验证 partial 状态。",
                "suggested_next_steps": ["创建模拟项目", "生成模拟执行计划"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            summary="模拟闭环本地结构化提取完成",
            suggested_next_steps=["创建模拟项目", "生成模拟执行计划"],
            analysis_mode="simulation_loop",
            model_name="simulation-local-v1",
            created_by=user.id,
            confirmed_by=user.id,
            confirmed_at=datetime.now(timezone.utc),
            metadata_json={"simulation": True, "loop_version": "1.0.0"},
        )
        db.add(analysis)

        evidence = await self.realm_service.create_evidence(db, user, str(registry.entity_id), {
            "claim": "模拟定位结论：从零开始建立GEO认知，需补齐行业赛道与渠道信息",
            "source_url": f"urn:simulation-loop:{intake.intake_code}",
            "source_name": "模拟闭环",
            "source_type": "simulation_loop",
            "truth_status": "synthetic",
            "excerpt": "模拟定位结论，仅用于基础设施验证",
        })

        project = await self.geo_project_service.create_project(db, user, {
            "realm_id": str(registry.id),
            "name": "模拟定位项目",
            "objective": "验证客户资料到定位结论再到项目计划的基础设施链路",
            "target_brand": "恒域模拟品牌",
            "target_product": "GEO模拟服务",
            "target_audience": "模拟目标客户",
            "scenario": "模拟闭环",
            "problems": ["从零开始建立GEO认知与转化路径"],
            "truth_status": "synthetic",
            "metadata": {
                "simulation": True,
                "simulation_level": "demo",
                "intake_id": str(intake.id),
            },
        })

        plan = await self.execution_plan_service.generate_plan(
            db, user, project["id"], simulation=True
        )

        intake.metadata_json = {
            **(intake.metadata_json or {}),
            "project_id": project["id"],
            "evidence_id": evidence["id"],
        }
        await db.commit()
        await db.refresh(intake)
        await self.gov.audit(
            db,
            user.id,
            "simulation_loop_run",
            "client_intake",
            str(intake.id),
            reason="simulation closed loop; no real metrics affected",
            actor_label=user.name,
            metadata={
                "simulation": True,
                "intake_id": str(intake.id),
                "project_id": project["id"],
            },
        )

        return {
            "simulation": True,
            "simulation_level": "demo",
            "loop_version": "1.0.0",
            "intake": {
                "id": str(intake.id),
                "intake_code": intake.intake_code,
                "status": intake.status,
                "source_truth_status": intake.source_truth_status,
            },
            "analysis": {
                "id": str(analysis.id),
                "status": analysis.status,
                "field_count": len(fields),
                "unknown_count": sum(1 for field in fields if field["status"] == "unknown"),
            },
            "evidence": evidence,
            "project": project,
            "plan": {
                "project_id": plan["project"]["id"],
                "work_item_count": len(plan["work_items"]),
                "simulation": True,
            },
            "position_conclusion": {
                "claim": "模拟定位结论：从零开始建立GEO认知，需补齐行业赛道与渠道信息",
                "truth_scope": "simulation",
                "unknowns": ["行业赛道", "现有渠道"],
            },
        }

    async def latest(self, db: AsyncSession, user, realm_ref: str) -> Dict:
        registry = await self._registry(db, realm_ref)
        if not registry:
            raise ValueError("realm not found")
        if not await self.realm_service._control(db, user, str(registry.entity_id)):
            raise PermissionError("realm owner/editor permission required")
        rows = (await db.execute(
            select(ClientIntake)
            .where(ClientIntake.realm_id == registry.id)
            .order_by(ClientIntake.created_at.desc())
        )).scalars().all()
        simulations = [
            row for row in rows
            if (row.metadata_json or {}).get("simulation") is True
        ]
        if not simulations:
            return {"simulation": True, "latest": None}
        latest = simulations[0]
        return {
            "simulation": True,
            "latest": {
                "id": str(latest.id),
                "intake_code": latest.intake_code,
                "status": latest.status,
                "source_truth_status": latest.source_truth_status,
                "project_id": (latest.metadata_json or {}).get("project_id"),
                "evidence_id": (latest.metadata_json or {}).get("evidence_id"),
                "created_at": latest.created_at.isoformat() if latest.created_at else None,
            },
        }


def get_simulation_loop_service() -> SimulationLoopService:
    return SimulationLoopService()
