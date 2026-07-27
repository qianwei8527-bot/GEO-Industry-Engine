from typing import Optional


class GEOScorer:
    @staticmethod
    def compute(entity_score: Optional[int]) -> dict:
        score = entity_score or 0
        return {"raw_score": score, "normalized": min(100, score), "level": GEOScorer._level(score)}

    @staticmethod
    def _level(score: int) -> str:
        if score >= 80: return "excellent"
        if score >= 60: return "good"
        if score >= 40: return "average"
        return "developing"
