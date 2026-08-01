"""C6.0 Real Node Onboarding tests: draft, validation, activation, idempotency, home."""
import sys, uuid
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.models.onboarding_session import OnboardingSession
from app.models.company import Company
from app.models.entity import Entity
from app.models.evidence import Evidence
from app.models.geo_event import GeoEvent
from app.models.identity_profile import IdentityProfile
from app.models.node_snapshot import NodeSnapshot
from app.models.growth_stage import GrowthStage
from app.services.node_activation import NodeActivationService
from app.universe.memory_engine import MemoryEngine
from app.universe.reputation_engine import ReputationEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine


def make_full_data(name="测试入驻企业"):
    return {
        "company_name": name,
        "description": "专注AI营销与GEO优化的测试企业",
        "region": "上海",
        "company_size": "50-200人",
        "website": "https://example.com",
        "industry_id": "ca076aa7-1bce-431a-b852-7e1a38381af6",
        "products": [
            {"name": "GEO优化服务", "core_capability": "AI内容优化", "product_type": "service"},
            {"name": "AI可见度分析", "core_capability": "数据分析", "product_type": "tool"},
        ],
        "evidence_items": [
            {"evidence_type": "official_website", "title": "官网服务展示", "source_url": "https://example.com", "source_name": "官网"},
            {"evidence_type": "customer_case", "title": "某客户案例", "source_url": "https://case.example.com", "source_name": "客户"},
        ],
        "goal_30d": "完成首次GEO检测",
        "goal_90d": "获得行业认证",
        "goal_180d": "进入行业Top30%",
    }


@pytest.fixture
def svc():
    return NodeActivationService()


class TestSessionDraft:
    def setup_method(self):
        MemoryEngine.reset()
        ReputationEngine.reset()
        RelationshipIntelligenceEngine.reset()

    async def test_create_and_restore(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            key = f"c60-draft-{uuid.uuid4().hex[:8]}"
            s = await svc.create_session(db, key, "草稿企业")
            await svc.save_draft(db, str(s.id), {"company_name": "草稿企业", "description": "草稿简介"}, 1)
            await svc.save_draft(db, str(s.id), {"products": [{"name": "产品A", "core_capability": "能力A"}]}, 3)
            got = await db.get(OnboardingSession, s.id)
            assert got.current_step == 3
            assert got.data_json["company_name"] == "草稿企业"
            assert got.data_json["products"][0]["name"] == "产品A"

    async def test_idempotent_create(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            key = f"c60-idem-{uuid.uuid4().hex[:8]}"
            s1 = await svc.create_session(db, key, "企业A")
            s2 = await svc.create_session(db, key, "企业A")
            assert s1.id == s2.id


class TestValidation:
    async def test_duplicate_company_detected(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            # existing company in DB: 星辰AI营销科技 (entity name)
            s = await svc.create_session(db, f"c60-dup-{uuid.uuid4().hex[:8]}", "星辰AI营销科技")
            await svc.save_draft(db, str(s.id), make_full_data("星辰AI营销科技"), 6)
            result = await svc.validate(db, s)
            assert any(w["type"] == "duplicate_company" for w in result["warnings"])

    async def test_invalid_evidence_url(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            data = make_full_data(f"URL企业{uuid.uuid4().hex[:6]}")
            data["evidence_items"] = [{"evidence_type": "media_report", "title": "报道", "source_url": "not-a-url"}]
            s = await svc.create_session(db, f"c60-url-{uuid.uuid4().hex[:8]}", data["company_name"])
            await svc.save_draft(db, str(s.id), data, 6)
            result = await svc.validate(db, s)
            assert result["valid"] is False
            assert any("URL" in i["message"] for i in result["issues"])

    async def test_missing_evidence_reported(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            data = make_full_data(f"缺证据企业{uuid.uuid4().hex[:6]}")
            data["evidence_items"] = []
            s = await svc.create_session(db, f"c60-mev-{uuid.uuid4().hex[:8]}", data["company_name"])
            await svc.save_draft(db, str(s.id), data, 6)
            result = await svc.validate(db, s)
            assert len(result["missing_evidence"]) >= 1

    async def test_partial_steps_allowed(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            s = await svc.create_session(db, f"c60-part-{uuid.uuid4().hex[:8]}", "")
            await svc.save_draft(db, str(s.id), {"company_name": "只有名称"}, 2)
            got = await db.get(OnboardingSession, s.id)
            assert got.data_json == {"company_name": "只有名称"}


class TestActivation:
    async def test_full_lifecycle(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            name = f"激活企业{uuid.uuid4().hex[:6]}"
            data = make_full_data(name)
            s = await svc.create_session(db, f"c60-act-{uuid.uuid4().hex[:8]}", name)
            await svc.save_draft(db, str(s.id), data, 6)
            result = await svc.activate(db, s)
            assert result["activation_status"] == "completed"
            assert result["lifecycle"]["observation"]["status"] == "completed"
            assert result["lifecycle"]["identity"]["status"] == "completed"
            assert result["lifecycle"]["position"]["status"] == "completed"
            assert result["lifecycle"]["reputation"]["status"] == "completed"
            assert result["lifecycle"]["possibility"]["status"] == "completed"
            assert result["lifecycle"]["connection"]["status"] == "completed"
            assert result["home_url"].startswith("/universe/home")

    async def test_activate_is_idempotent(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            name = f"幂等企业{uuid.uuid4().hex[:6]}"
            data = make_full_data(name)
            key = f"c60-idemact-{uuid.uuid4().hex[:8]}"
            s = await svc.create_session(db, key, name)
            await svc.save_draft(db, str(s.id), data, 6)
            r1 = await svc.activate(db, s)
            node_id = r1["node_id"]
            ev_count = (await db.execute(select(func.count(GeoEvent.id)).where(GeoEvent.source_node_type == "session"))).scalar() or 0
            r2 = await svc.activate(db, s)
            assert r2["node_id"] == node_id
            # No duplicate company
            companies = (await db.execute(select(func.count(Company.id)).where(Company.name == name))).scalar() or 0
            assert companies == 1

    async def test_home_can_read_new_node(self, svc):
        factory = _get_session_factory()
        async with factory() as db:
            name = f"Home企业{uuid.uuid4().hex[:6]}"
            data = make_full_data(name)
            s = await svc.create_session(db, f"c60-home-{uuid.uuid4().hex[:8]}", name)
            await svc.save_draft(db, str(s.id), data, 6)
            result = await svc.activate(db, s)
            node_id = result["node_id"]
            # Context engine can understand the new node (Home reads this)
            from app.universe.context_engine import get_context_engine
            ctx = get_context_engine().understand(node_id, "company", {"name": name})
            assert ctx.identity["name"] == name
            assert ctx.current_position.get("position", {}).get("growth_stage") is not None

    async def test_config_loaded(self, svc):
        assert svc.config.get("version") == "1.0.0"
        assert len(svc.config.get("steps", [])) == 6
        assert len(svc.config.get("activation_stages", [])) == 10
        assert svc.config["evidence_confidence"]["official_website"] == 0.8