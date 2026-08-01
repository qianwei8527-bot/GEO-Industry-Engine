"""C6.4 GEO visibility tests: fake provider, answer artifacts, metrics, no reputation change."""
import sys, uuid
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.services.geo_visibility import GEOVisibilityService
from app.models.geo_visibility import AIAnswerArtifact, VisibilityResult, QuestionSet
from app.models.company import Company
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine
from app.universe.memory_engine import MemoryEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine


def fake_chat_factory(node_id_hint=""):
    async def chat(question, node_id, model):
        # Deterministic fake: mentions the node when question asks for providers
        if "推荐" in question or "服务商" in question:
            return f"1. 「{node_id}」是GEO服务商，来源 https://example.com/{node_id}\n2. 其他服务商 https://other.example.com"
        return "GEO是生成式引擎优化，来源 https://geo.example.com/explain"
    return chat


async def real_node(db):
    row = (await db.execute(select(Company.id).limit(1))).scalars().first()
    return str(row) if row else str(uuid.uuid4())


class TestGEOVisibility:
    def setup_method(self):
        ReputationEngine.reset(); MemoryEngine.reset(); RelationshipIntelligenceEngine.reset()

    async def test_provider_not_configured(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = GEOVisibilityService()
            status = svc.provider_status()
            # No real keys in test env -> at least one "未配置"
            assert status != {}
            result = await svc.execute(db, str(uuid.uuid4()), provider="openai")
            assert result.get("status") == "blocked"

    async def test_fake_run_saves_answers_and_metrics(self):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await real_node(db)
            svc = GEOVisibilityService(chat_fn=fake_chat_factory())
            await svc.sync_question_sets(db)
            # Inject fake configured state by monkeypatching provider_status
            svc.provider_status = lambda: {"fake": {"configured": True, "model": "fake-model", "status": "ready", "observation_mode": "closed_book", "citation": "urls_in_text_only"}}
            svc.budget_cfg["pricing_per_1k_tokens"]["fake"] = {"fake-model": {"input": 0.001, "output": 0.001}}
            svc.budget_cfg["per_run_budget"] = 10.0
            result = await svc.execute(db, nid, provider="fake")
            assert result["status"] == "completed"
            assert result["answers"] >= 1
            arts = (await db.execute(select(AIAnswerArtifact).where(AIAnswerArtifact.provider == "fake"))).scalars().all()
            assert len(arts) >= 1
            assert arts[0].raw_answer
            assert arts[0].answer_hash
            vis = (await db.execute(select(VisibilityResult).where(VisibilityResult.node_id == nid))).scalars().all()
            assert len(vis) >= 1

    async def test_ai_answer_does_not_change_reputation(self):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await real_node(db)
            re = get_reputation_engine()
            re.record_event(nid, "company", "certification_passed", "ISO", "government")
            re.recalculate(nid, "company")
            before = re.get_profile(nid).overall_score
            svc = GEOVisibilityService(chat_fn=fake_chat_factory())
            svc.provider_status = lambda: {"fake": {"configured": True, "model": "m", "status": "ready", "observation_mode": "closed_book", "citation": "urls_in_text_only"}}
            svc.budget_cfg.setdefault("pricing_per_1k_tokens", {})["fake"] = {"m": {"input": 0.001, "output": 0.001}}
            svc.budget_cfg["per_run_budget"] = 10.0
            await svc.execute(db, nid, provider="fake")
            after = re.get_profile(nid).overall_score
            assert after == before

    async def test_citations_parsed(self):
        factory = _get_session_factory()
        async with factory() as db:
            nid = await real_node(db)
            svc = GEOVisibilityService(chat_fn=fake_chat_factory())
            svc.provider_status = lambda: {"fake": {"configured": True, "model": "m", "status": "ready", "observation_mode": "closed_book", "citation": "urls_in_text_only"}}
            svc.budget_cfg.setdefault("pricing_per_1k_tokens", {})["fake"] = {"m": {"input": 0.001, "output": 0.001}}
            svc.budget_cfg["per_run_budget"] = 10.0
            await svc.execute(db, nid, provider="fake", question_keys=["provider_recommendation_1"])
            arts = (await db.execute(select(AIAnswerArtifact).where(AIAnswerArtifact.provider == "fake"))).scalars().all()
            assert any(a.citations for a in arts)
            assert any("https://" in (c.get("cited_url") or "") for a in arts for c in (a.citations or []))

    async def test_three_nodes_different(self):
        factory = _get_session_factory()
        async with factory() as db:
            rows = (await db.execute(select(Company.id).limit(3))).scalars().all()
            if len(rows) < 3:
                pytest.skip("need 3 companies")
            for i, nid in enumerate(rows):
                svc = GEOVisibilityService(chat_fn=fake_chat_factory())
                svc.provider_status = lambda: {"fake": {"configured": True, "model": "m", "status": "ready", "observation_mode": "closed_book", "citation": "urls_in_text_only"}}
                svc.budget_cfg.setdefault("pricing_per_1k_tokens", {})["fake"] = {"m": {"input": 0.001, "output": 0.001}}
                svc.budget_cfg["per_run_budget"] = 10.0
                await svc.execute(db, str(nid), provider="fake", question_keys=["provider_recommendation_1"])
            arts = (await db.execute(select(AIAnswerArtifact).where(AIAnswerArtifact.provider == "fake"))).scalars().all()
            # Distinct raw answers (each mentions its own node id)
            assert len({a.raw_answer for a in arts}) >= 2

    async def test_sync_question_sets(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = GEOVisibilityService()
            n = await svc.sync_question_sets(db)
            qs = (await db.execute(select(func.count(QuestionSet.id)))).scalar()
            assert qs >= 10