from typing import List, Tuple
from app.models.company import Company


class RelevanceScorer:
    @staticmethod
    def score_companies(query: str, companies: List[Company]) -> List[Tuple[Company, float]]:
        if not query.strip():
            return [(c, 0.5) for c in companies]
        query_lower = query.lower()
        results = []
        for c in companies:
            score = 0.0
            if c.name and query_lower in c.name.lower():
                score += 0.4
            if c.description and query_lower in c.description.lower():
                score += 0.3
            if c.website and query_lower in c.website.lower():
                score += 0.2
            results.append((c, min(score, 1.0)))
        results.sort(key=lambda x: x[1], reverse=True)
        return results
