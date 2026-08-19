"""V10-P0 GEO Project closed loop tests."""

import sys
import uuid
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

from sqlalchemy import select, delete

from app.database import _get_session_factory
from app.models.user import User, UserRole
from app.models.entity import Entity
from app.models.brand import Brand
from app.models.company import Company
from app.models.governance import NodeMembership
from app.models.realm import RealmRegistry
from app.models.evidence import Evidence
from app.models.evidence_claim import EvidenceClaim
from app.models.geo_project import (
    GeoProject,
    ProjectWorkItem,
    ProjectArtifact,
    ToolExecutionRecord,
    ProjectOutcome,
)
from app.services.realm_service import get_realm_service
from app.services.geo_project_service import get_geo_project_service
from app.services.evidence_claim import get_evidence_claim_service
from app.services.trust_foundation import TrustFoundationService


def make_user(db, email):
    u = User(email=email, password_hash="x", name="域主", role=UserRole.ENTERPRISE)
    db.add(u)
    return u


async def _cleanup(db, entity_ids, user_ids, project_ids):
    for pid in project_ids:
        await db.execute(delete(ProjectOutcome).where(ProjectOutcome.project_id == pid))
        await db.execute(delete(ToolExecutionRecord).where(ToolExecutionRecord.project_id == pid))
        await db.execute(delete(ProjectArtifact).where(ProjectArtifact.project_id == pid))
        await db.execute(delete(ProjectWorkItem).where(ProjectWorkItem.project_id == pid))
        await db.execute(delete(GeoProject).where(GeoProject.id == pid))
    for eid in entity_ids:
        await db.execute(delete(EvidenceClaim).where(EvidenceClaim.subject_id == str(eid)))
        await db.execute(delete(Evidence).where(Evidence.entity_id == eid))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(eid)))
        await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == eid))
        await db.execute(delete(Brand).where(Brand.id == eid))
        await db.execute(delete(Company).where(Company.id == eid))
        await db.execute(delete(Entity).where(Entity.id == eid))
    for uid in user_ids:
        await db.execute(delete(User).where(User.id == uid))
    await db.commit()


class TestGeoProjectClosedLoop:
    async def test_project_tool_artifact_outcome_timeline(self):
        factory = _get_session_factory()
        async with factory() as db:
            user = make_user(db, f"project-{uuid.uuid4().hex[:8]}@x.com")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            realm_svc = get_realm_service()
            ws = await realm_svc.create_enterprise(db, user, {
                "name": "V10 项目域", "website": f"https://{uuid.uuid4().hex[:8]}.test"
            })
            entity_id = uuid.UUID(ws["identity"]["id"])
            registry = (await db.execute(
                select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
            )).scalars().first()
            project_svc = get_geo_project_service()
            project = await project_svc.create_project(db, user, {
                "realm_id": str(registry.id),
                "name": "科技特长生 GEO 首项目",
                "target_brand": "V10 教育科技",
                "target_audience": "学生家长",
                "scenario": "科技特长生升学规划",
                "problems": ["AI 搜索不可见"],
                "ai_platforms": ["ChatGPT", "豆包"],
                "question_set": ["科技特长生如何规划"],
                "competitors": ["竞品A"],
                "expected_outcome": "品牌出现在 AI 回答中",
            })
            project_id = project["id"]
            try:
                assert project["truth_status"] == "observed"
                assert project["may_affect_real_metrics"] is False
                item = await project_svc.create_work_item(db, user, project_id, {
                    "work_type": "diagnosis", "title": "AI 可见性诊断",
                    "status": "completed",
                    "input_manifest": {"target_brand": "V10 教育科技"},
                    "output_manifest": {"diagnosis": "观察结果"},
                })
                auth = await realm_svc.create_authorization(db, user, str(entity_id), {
                    "source_name": "官网", "source_url": f"https://{uuid.uuid4().hex[:8]}.test",
                    "use_scope": "ai_tools",
                    "grantee_type": "provider",
                    "provider": "universe",
                    "tool_name": "geo_visibility",
                })
                run = await project_svc.create_tool_execution(db, user, project_id, {
                    "provider": "universe", "tool_name": "geo_visibility",
                    "authorization_id": auth["id"],
                    "model_name": "rule-based", "model_version": "1.0",
                    "input_manifest": {"question_set": project["question_set"]},
                    "output_manifest": {"visibility": "not_observed"},
                    "cost": 0.0,
                })
                assert run["config_version"] == "1.1.0"
                assert run["execution_source"] == "declared"
                assert run["execution_status"] == "declared"
                assert run["config_hash"]
                artifact = await project_svc.create_artifact(db, user, project_id, {
                    "work_item_id": item["id"], "artifact_type": "report",
                    "title": "首份诊断报告", "content_json": {"summary": "尚无 verified 证据"},
                    "status": "draft", "citations": [],
                })
                pending = await project_svc.create_outcome(db, user, project_id, {
                    "outcome_type": "visibility_observation",
                    "claim_text": "品牌在 AI 回答中未被观察到",
                })
                assert pending["status"] == "pending"
                assert pending["truth_status"] == "observed"
                ev = await realm_svc.create_evidence(db, user, str(entity_id), {
                    "claim": "官网页面包含科技特长生内容", "source_url": f"https://{uuid.uuid4().hex[:8]}.test",
                    "source_type": "official_website",
                })
                await TrustFoundationService().verify_evidence(
                    db, ev["id"], str(uuid.uuid4()),
                    method="universe_record_crosscheck", result="approved"
                )
                ev_refresh = await db.get(Evidence, uuid.UUID(ev["id"]))
                claim = await get_evidence_claim_service().create_claim(
                    db, ev["id"], "entity", str(entity_id), "appears_in_ai_answer",
                    "concept", "ai_answer_mention",
                    object_value="AI回答中出现V10教育科技",
                    claim_text="AI回答中出现V10教育科技",
                    metadata={"project_id": project_id, "artifact_id": artifact["id"]},
                )
                claim_row = await db.get(EvidenceClaim, uuid.UUID(claim["id"]))
                claim_row.may_affect_real_metrics = ev_refresh.may_affect_real_metrics
                await db.commit()
                await get_evidence_claim_service().verify_claim(
                    db, claim["id"], str(uuid.uuid4()), method="structured_review", result="approved"
                )
                verified = await project_svc.create_outcome(db, user, project_id, {
                    "outcome_type": "visibility_observation",
                    "claim_text": "AI回答中出现V10教育科技",
                    "evidence_claim_id": claim["id"],
                })
                assert verified["status"] == "verified"
                assert verified["truth_status"] == "verified"
                timeline = await project_svc.timeline(db, user, project_id)
                assert any(t["type"] == "tool_execution" for t in timeline)
                assert any(t["type"] == "artifact" for t in timeline)
                assets = await project_svc.project_assets(db, user, project_id)
                assert any(a["title"] == "首份诊断报告" for a in assets["artifacts"])
            finally:
                await _cleanup(db, [entity_id], [user.id], [uuid.UUID(project_id)])
