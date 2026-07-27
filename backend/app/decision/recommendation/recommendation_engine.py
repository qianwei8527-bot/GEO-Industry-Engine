from app.context.schemas.context_schema import CompanyContext


class RecommendationEngine:
    @staticmethod
    async def generate(context: CompanyContext, scores: dict) -> list:
        recommendations = []
        vis = scores.get("visibility", {}).get("score", 0)
        trust = scores.get("trust", {}).get("score", 0)
        cap = len(context.capabilities)
        rel = len(context.relationships)

        # Partnership recommendation
        if rel < 3:
            recommendations.append({
                "type": "partnership", "priority": "high",
                "title": "Expand relationship network",
                "reason": f"Currently {rel} relationships; aim for 5+ for better visibility",
            })

        # Capability recommendation
        if cap < 3:
            recommendations.append({
                "type": "capability", "priority": "high",
                "title": "Document core capabilities",
                "reason": f"Only {cap} capabilities documented; at least 3 recommended",
            })

        # Trust recommendation
        if trust < 50:
            recommendations.append({
                "type": "trust", "priority": "medium",
                "title": "Build trust signals",
                "reason": "Trust score is low; add certifications, customer cases, third-party validation",
            })

        # Visibility recommendation
        if vis < 50:
            recommendations.append({
                "type": "visibility", "priority": "high",
                "title": "Improve AI visibility",
                "reason": "GEO Visibility Score is below average; focus on entity completeness and evidence",
            })

        if not recommendations:
            recommendations.append({
                "type": "maintain", "priority": "low",
                "title": "Maintain current position",
                "reason": "All scores are healthy. Continue monitoring and updating content.",
            })

        return recommendations
