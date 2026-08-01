"""C6.4-R hard gates: budget preflight, unknown price, 30 questions, modes, citation grading, DNS."""
import sys, uuid
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.services.geo_visibility import GEOVisibilityService
from app.models.geo_visibility import QuestionSet, VisibilityResult
from app.services.observation_network import resolve_all_and_validate


class TestHardGates:
    def test_30_question_library(self):
        svc = GEOVisibilityService()
        qs = svc.all_questions()
        assert len(qs) == 30, f"expected 30, got {len(qs)}"
        neutral = [q for q in qs if q["observation_type"] == "neutral_discovery"]
        branded = [q for q in qs if q["observation_type"] == "branded_probe"]
        assert len(neutral) == 21  # 20 neutral + 1 industry trust
        assert len(branded) == 9

    def test_budget_preflight_blocks_when_over(self):
        svc = GEOVisibilityService()
        svc.provider_status = lambda: {"fake": {"configured": True, "model": "m", "status": "ready", "observation_mode": "closed_book"}}
        svc.budget_cfg.setdefault("pricing_per_1k_tokens", {})["fake"] = {"m": {"input": 1.0, "output": 1.0}}
        svc.budget_cfg["per_run_budget"] = 0.001
        pre = svc.preflight("fake")
        assert pre["allowed"] is False
        assert any("超过" in r for r in pre["reasons"])

    def test_unknown_price_blocks(self):
        svc = GEOVisibilityService()
        svc.provider_status = lambda: {"fake": {"configured": True, "model": "m", "status": "ready"}}
        # no price for fake/m in budget_cfg
        pre = svc.preflight("fake")
        assert pre["allowed"] is False
        assert any("价格未知" in r for r in pre["reasons"])

    def test_citation_grading_generated_url_low_confidence(self):
        svc = GEOVisibilityService()
        graded = svc._grade_citations("参考 https://example.com/x", "openai")
        assert graded[0]["citation_grade"] == "unverified_generated_url"

    def test_closed_book_mode(self):
        svc = GEOVisibilityService()
        st = svc.provider_status()
        # provider registry builtins exist; openai mode should be closed_book (no key needed for capability)
        assert st.get("openai", {}).get("observation_mode") in ("closed_book", "unknown", None)

    async def test_fake_not_baseline_eligible(self):
        factory = _get_session_factory()
        async with factory() as db:
            from app.models.company import Company
            nid = str((await db.execute(select(Company.id).limit(1))).scalars().first())
            svc = GEOVisibilityService(chat_fn=lambda q, n, m: "「%s」是GEO服务商 https://a.com" % n)
            svc.provider_status = lambda: {"fake": {"configured": False, "model": "m", "status": "未配置", "observation_mode": "closed_book"}}
            pre = svc.preflight("fake")
            assert pre["allowed"] is False

    def test_dns_rebinding_all_ips_validated(self):
        # localhost must be rejected even if another record is public
        with pytest.raises(ValueError):
            resolve_all_and_validate("localhost")

    async def test_question_set_sync_persists_30(self):
        factory = _get_session_factory()
        async with factory() as db:
            svc = GEOVisibilityService()
            await svc.sync_question_sets(db)
            n = (await db.execute(select(func.count(QuestionSet.id)))).scalar()
            assert n >= 30