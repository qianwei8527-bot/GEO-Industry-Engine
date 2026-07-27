class ReasonGenerator:
    @staticmethod
    def for_visibility(score: float, factors: dict) -> dict:
        reasons = []
        actions = []
        if factors.get("entity_quality", 0) >= 0.7:
            reasons.append("Company profile is complete")
        else:
            actions.append("Complete company profile: add description and website")
            reasons.append("Company profile needs improvement")
        if factors.get("evidence_score", 0) >= 0.5:
            reasons.append("Verified evidence available")
        else:
            actions.append("Provide verifiable evidence for capabilities")
        if factors.get("capability_match", 0) >= 0.4:
            reasons.append("Capabilities are documented")
        else:
            actions.append("Document at least 3 core capabilities")
        if factors.get("relationship_density", 0) >= 0.3:
            reasons.append("Active relationship network")
        if not actions:
            actions.append("Maintain current visibility level")
        return {"reasons": reasons[:5], "actions": actions[:5]}

    @staticmethod
    def for_industry_index(score: float, factors: dict) -> dict:
        reasons = [f"Industry density: {factors.get('company_density', 0):.1%}"]
        actions = []
        if factors.get("event_frequency", 0) < 0.3:
            actions.append("Encourage more industry events and news")
        return {"reasons": reasons, "actions": actions or ["Monitor industry trends"]}

    @staticmethod
    def for_growth(score: float, factors: dict) -> dict:
        return {"reasons": [f"Growth potential score: {score:.1f}"],
                "actions": ["Focus on high-scoring areas for quick wins"]}
