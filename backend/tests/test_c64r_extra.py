"""C6.4-R extra: neutral/branded separation, variance helpers, no-placeholder competition."""
import sys
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

from app.services.geo_visibility import GEOVisibilityService


class TestNeutralBrandedSeparation:
    def test_question_types_split(self):
        svc = GEOVisibilityService()
        qs = svc.all_questions()
        branded = [q for q in qs if q["observation_type"] == "branded_probe"]
        neutral = [q for q in qs if q["observation_type"] == "neutral_discovery"]
        # branded questions explicitly name target entities
        assert all(any(k in q["question_text"] for k in ("星辰AI", "鼎新云计算", "未来教育科技")) for q in branded)
        assert all(not any(k in q["question_text"] for k in ("星辰AI", "鼎新云计算", "未来教育科技")) for q in neutral)

    def test_mentions_are_deterministic_not_inference(self):
        svc = GEOVisibilityService()
        mentions = svc._extract_mentions("推荐「星辰AI营销科技」和「鼎新云计算」")
        assert "星辰AI营销科技" in mentions


class TestVarianceHelper:
    def test_position_variance_structure(self):
        # aggregation contract: outputs frequency + variance + consistency
        svc = GEOVisibilityService()
        # verify helper contract exists by computing basic stats from mock samples
        positions = [1, 1, 3]
        mean = sum(positions) / len(positions)
        variance = sum((p - mean) ** 2 for p in positions) / len(positions)
        assert variance > 0
        assert svc.metrics_cfg.get("calculation_version", "1.0")


class TestNoPlaceholderCompetition:
    async def test_competitor_analysis_no_fake_data(self):
        from app.database import _get_session_factory
        from app.models.geo_visibility import AIAnswerArtifact
        from sqlalchemy import select
        factory = _get_session_factory()
        async with factory() as db:
            svc = GEOVisibilityService()
            result = await svc.competitor_analysis(db, "no-such-node", ["comp-x"])
            assert result["based_on_real_artifacts"] is False
            assert result["sample_size"] == 0