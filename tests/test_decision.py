import pytest
from app.decision.scoring.calculator import ScoreCalculator
from app.decision.scoring.weights import WeightsLoader


class TestScoreCalculator:
    def test_weighted_sum(self):
        r = ScoreCalculator.weighted_sum({"a": 0.8, "b": 0.6}, {"a": 0.5, "b": 0.5})
        assert r == 70.0

    def test_weighted_sum_zero(self):
        r = ScoreCalculator.weighted_sum({}, {})
        assert r == 0.0

    def test_normalize(self):
        r = ScoreCalculator.normalize(50, 0, 100)
        assert r == 50.0

    def test_level(self):
        assert ScoreCalculator.level(85, {"high": 80}) == "excellent"
        assert ScoreCalculator.level(65, {"high": 80, "medium": 60}) == "good"


from app.decision.models.geo_visibility import GEOVisibilityScore

class TestDecisionModels:
    def test_visibility_levels(self):
        from app.decision.models.base import DecisionModel
        m = GEOVisibilityScore()
        assert m._level(85) == "excellent"
        assert m._level(65) == "good"
        assert m._level(45) == "average"
        assert m._level(15) == "developing"
