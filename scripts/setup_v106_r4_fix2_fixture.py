#!/usr/bin/env python3
"""Create an isolated V10.6-R4-FIX2 real fixture for screenshots and E2E checks."""

import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select

from app.core.security import create_access_token
from app.database import _get_session_factory
from app.models.realm import RealmRegistry
from app.models.user import User, UserRole
from app.services.geo_project_service import get_geo_project_service
from app.services.governance import get_governance_service
from app.services.intake_service import get_intake_service
from app.services.issue_service import get_issue_service
from app.services.project_plan_service import get_project_plan_service
from app.services.realm_service import get_realm_service


OWNER_TEMPLATE = {
    "phases": [{"phase": "阶段一", "tasks": [
        {"task_key": "t1", "title": "发布渠道权限复核", "purpose": "验证真实闭环",
         "description": "用于 R4-FIX2 截图与 E2E", "expected_output": "权限结论",
         "acceptance_criteria": "问题已验证", "required_materials": ["授权记录"],
         "risks": ["权限误判"], "execution_mode": "owner_review"},
    ]}],
}


async def main() -> None:
    factory = _get_session_factory()
    async with factory() as db:
        owner = User(
            email=f"r4-fix2-shot-{uuid.uuid4().hex[:8]}@example.com",
            password_hash="x",
            name="R4真实域主",
            role=UserRole.ENTERPRISE,
        )
        outsider = User(
            email=f"r4-fix2-outside-{uuid.uuid4().hex[:8]}@example.com",
            password_hash="x",
            name="R4外部用户",
            role=UserRole.INDIVIDUAL,
        )
        db.add_all([owner, outsider])
        await db.commit()
        await db.refresh(owner)
        await db.refresh(outsider)

        ws = await get_realm_service().create_enterprise(db, owner, {
            "name": "R4真实演示域",
            "website": f"https://{uuid.uuid4().hex[:8]}.test",
        })
        entity_id = uuid.UUID(ws["identity"]["id"])
        registry = (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
        )).scalars().first()

        intake_svc = get_intake_service()
        intake = await intake_svc.create_intake(db, owner, str(registry.id), {
            "pasted_text": (
                "品牌名称：R4演示品牌\n企业主体：R4演示企业\n产品：渠道权限管理服务\n"
                "问题：发布渠道权限不足导致执行阻塞\n"
            ),
            "files": [],
        })
        await intake_svc.analyze_intake(db, owner, intake["id"])
        await intake_svc.start_review(db, owner, intake["id"])
        await intake_svc.update_profile(db, owner, intake["id"], {"target_customer": "R4真实客户"})
        await intake_svc.confirm_profile(db, owner, intake["id"])
        positioning = await intake_svc.generate_positioning(db, owner, intake["id"])
        await intake_svc.confirm_positioning(
            db, owner, intake["id"],
            {"priority_direction": "先补齐渠道权限闭环"},
            expected_version=positioning["version"],
        )
        project = await get_geo_project_service().create_project_from_positioning(
            db, owner, intake["id"], confirmed=True,
        )
        plan = await get_project_plan_service().generate_plan(
            db, owner, project["id"], "owner_defined", "owner-defined", OWNER_TEMPLATE,
        )
        view = await get_project_plan_service().confirm_plan(
            db, owner, project["id"], True, plan["plan_version"],
        )
        task = view["tasks"][0]

        issue_svc = get_issue_service()
        issue = await issue_svc.create_issue(db, owner, str(registry.id), {
            "original_text": "发布渠道权限不足导致无法按计划执行",
            "title": "发布渠道权限不足",
            "project_id": project["id"],
            "work_item_id": task["id"],
            "source_type": "plan_task",
            "idempotency_key": f"issue-{uuid.uuid4().hex[:8]}",
        })
        await issue_svc.update_issue(db, owner, issue["id"], {"status": "triaged"}, expected_version=1)
        await issue_svc.update_issue(db, owner, issue["id"], {"status": "in_progress"}, expected_version=2)
        await issue_svc.add_attempt(
            db, owner, issue["id"],
            {"method": "检查发布配置", "result": "failed", "failure_reason": "账号授权不足",
             "tool": "toolA", "action": "检查发布配置"},
            expected_version=3,
        )
        await issue_svc.add_attempt(
            db, owner, issue["id"],
            {"method": "重新授权并发布", "result": "success", "tool": "toolB",
             "action": "域主重新授权后重试"},
            expected_version=4,
        )
        await issue_svc.update_issue(
            db, owner, issue["id"],
            {"final_solution": "域主补授权后重新发布", "applicability_boundary": "仅限内部账号"},
            expected_version=5,
        )
        resolved = await issue_svc.resolve_issue(db, owner, issue["id"], expected_version=6)
        verified = await issue_svc.verify_issue(db, owner, resolved["id"], expected_version=7)
        skill = await issue_svc.generate_skill(db, owner, [verified["id"]])
        skillless = await issue_svc.create_issue(db, owner, str(registry.id), {
            "original_text": "工具调用超时导致批量导出中断",
            "title": "工具调用超时",
            "project_id": project["id"],
            "work_item_id": task["id"],
            "source_type": "plan_task",
            "idempotency_key": f"issue-{uuid.uuid4().hex[:8]}",
        })
        await issue_svc.update_issue(db, owner, skillless["id"], {"status": "triaged"}, expected_version=1)
        await issue_svc.update_issue(db, owner, skillless["id"], {"status": "in_progress"}, expected_version=2)
        resolved2 = await issue_svc.resolve_issue(db, owner, skillless["id"], expected_version=3)
        await issue_svc.verify_issue(db, owner, resolved2["id"], expected_version=4)
        open_issue = await issue_svc.create_issue(db, owner, str(registry.id), {
            "original_text": "客户资料中缺少联系方式与渠道明细",
            "title": "客户资料缺少联系方式",
            "project_id": project["id"],
            "work_item_id": task["id"],
            "source_type": "plan_task",
            "idempotency_key": f"issue-{uuid.uuid4().hex[:8]}",
        })

        print(json.dumps({
            "realm_id": str(registry.id),
            "realm_entity_id": str(entity_id),
            "project_id": project["id"],
            "task_id": str(task["id"]),
            "issue_id": issue["id"],
            "issue_title": "发布渠道权限不足",
            "skillless_issue_id": skillless["id"],
            "skillless_issue_title": "工具调用超时",
            "open_issue_id": open_issue["id"],
            "open_issue_title": "客户资料缺少联系方式",
            "skill_id": skill["id"],
            "owner_token": create_access_token(owner.id),
            "outsider_token": create_access_token(outsider.id),
            "owner_email": owner.email,
            "outsider_email": outsider.email,
        }, ensure_ascii=False))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
