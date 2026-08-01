import asyncio, sys, uuid
sys.path.insert(0, r"D:\GEO-Industry-Engine\backend")

from sqlalchemy import select, func
from app.database import _get_session_factory
from app.services.learning_loop import LearningLoopService
from app.models.evidence import Evidence
from app.models.company import Company
from app.models.capability import Capability
from app.models.candidate_change import CandidateChange
from app.universe.reputation_engine import get_reputation_engine, ReputationEngine
from app.universe.memory_engine import MemoryEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine

NODES = {
    "xingchen": "b4578afd-4454-4000-a4a3-8075d70d2f79",
    "dingxin": "3361adb3-0aef-451f-a834-fb9e0b8f29bb",
    "weilai": "ed800951-9977-41a5-8ef4-6335d83fe2fc",
}

async def main():
    ReputationEngine.reset(); MemoryEngine.reset(); RelationshipIntelligenceEngine.reset()
    svc = LearningLoopService()
    factory = _get_session_factory()

    print("=" * 60)
    print("C6.1 THREE REAL SCENARIOS")
    print("=" * 60)

    # ── Scenario A: 星辰 verified media report ──
    print("\n[A] 星辰AI营销科技 — 新增经过验证的媒体报道")
    async with factory() as db:
        re = get_reputation_engine()
        nid = NODES["xingchen"]
        rep_before = re.get_profile(nid)
        ev_before = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == nid))).scalar() or 0

        cc = await svc.create_observation(db, {
            "node_id": nid, "change_type": "user_evidence",
            "source_type": "admin", "source_id": f"media-{uuid.uuid4().hex[:6]}",
            "evidence_summary": "获得AI营销行业权威媒体报道",
            "proposed_value": {
                "title": "AI营销行业权威媒体报道", "source_url": "https://news.example.com/xingchen",
                "source_name": "行业媒体", "evidence_type": "media_report",
                "confidence_level": 0.8, "occurred_at": "2026-07-01",
            },
        })
        await svc.approve(db, str(cc.id), "admin", "已验证来源")
        # Simulate verification by updating evidence to verified
        applied = await svc.apply(db, str(cc.id), "admin")
        ev_after = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == nid))).scalar() or 0
        rep_after = re.get_profile(nid)
        print(f"  evidence: {ev_before} -> {ev_after}")
        print(f"  reputation: {rep_before.overall_score if rep_before else 'N/A'} -> {rep_after.overall_score if rep_after else 'N/A'}")
        print(f"  change: {applied.review_status} engines={applied.affected_engines}")

    # ── Scenario B: 鼎新 capability update ──
    print("\n[B] 鼎新云计算 — 新增有证据支持的核心能力")
    async with factory() as db:
        nid = NODES["dingxin"]
        caps_before = (await db.execute(select(func.count(Capability.id)).where(Capability.company_id == nid))).scalar() or 0
        cc = await svc.create_observation(db, {
            "node_id": nid, "change_type": "profile_update",
            "source_type": "admin", "source_id": f"cap-{uuid.uuid4().hex[:6]}",
            "evidence_summary": "新增数据合规能力，有企业认证证据",
            "proposed_value": {"capabilities": [{"name": "数据合规", "core_capability": "合规治理", "product_type": "service"}]},
        })
        await svc.approve(db, str(cc.id), "admin", "证据支持")
        applied = await svc.apply(db, str(cc.id), "admin")
        caps_after = (await db.execute(select(func.count(Capability.id)).where(Capability.company_id == nid))).scalar() or 0
        print(f"  capabilities: {caps_before} -> {caps_after}")
        print(f"  recomputed: {applied.applied_result.get('recomputed') if applied.applied_result else []}")
        print(f"  applied: {applied.review_status}")
        hist = await svc.get_learning_history(db, nid)
        print(f"  learning history entries: {len(hist)}")

    # ── Scenario C: 未来教育 unverifiable case ──
    print("\n[C] 未来教育科技 — 提交无法验证的客户案例")
    async with factory() as db:
        re = get_reputation_engine()
        nid = NODES["weilai"]
        rep_before = re.get_profile(nid)
        ev_before = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == nid))).scalar() or 0
        cc = await svc.create_observation(db, {
            "node_id": nid, "change_type": "user_evidence",
            "source_type": "user", "source_id": f"case-{uuid.uuid4().hex[:6]}",
            "evidence_summary": "声称服务100所学校，无来源可验证",
            "proposed_value": {"title": "服务100所学校", "source_url": "https://unverified.example.com", "evidence_type": "customer_case"},
        })
        # self-report -> must be PENDING_REVIEW, not applied
        assert cc.review_status == "PENDING_REVIEW", cc.review_status
        await svc.reject(db, str(cc.id), "admin", "无法验证来源")
        ev_after = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == nid))).scalar() or 0
        rep_after = re.get_profile(nid)
        rejected = await svc.get_change(db, str(cc.id))
        print(f"  review_status: {rejected['review_status']}")
        print(f"  rejection_reason: {rejected['rejection_reason']}")
        print(f"  evidence: {ev_before} -> {ev_after} (rejected adds nothing)")
        print(f"  reputation: {rep_before.overall_score if rep_before else 'N/A'} -> {rep_after.overall_score if rep_after else 'N/A'} (unchanged)")

    print("\n" + "=" * 60)
    print("SCENARIOS COMPLETE")
    print("=" * 60)

asyncio.run(main())
