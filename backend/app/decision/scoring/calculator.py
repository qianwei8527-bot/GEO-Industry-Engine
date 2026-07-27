class ScoreCalculator:
    @staticmethod
    def weighted_sum(factors: dict, weights: dict) -> float:
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        weighted = sum(factors.get(k, 0) * v for k, v in weights.items())
        return round(min(100.0, weighted / total_weight * 100), 1)

    @staticmethod
    def normalize(value: float, min_val: float, max_val: float) -> float:
        if max_val <= min_val:
            return 50.0
        return round((value - min_val) / (max_val - min_val) * 100, 1)

    @staticmethod
    def level(score: float, thresholds: dict) -> str:
        if score >= thresholds.get("high", 80): return "excellent"
        if score >= thresholds.get("medium", 60): return "good"
        if score >= thresholds.get("low", 30): return "average"
        return "developing"
