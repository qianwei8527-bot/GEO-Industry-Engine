from app.decision.models.base import DecisionModel
from app.decision.scoring.weights import WeightsLoader
from app.decision.scoring.calculator import ScoreCalculator
from app.decision.explanation.reason_generator import ReasonGenerator
from app.context.schemas.context_schema import CompanyContext


class GEOVisibilityScore(DecisionModel):
    async def calculate(self, context: CompanyContext) -> dict:
        weights = WeightsLoader.get_weights("geo_visibility")
        factors = {}

        # Entity quality: completeness of company profile
        c = context.company
        quality = 0.0
        if c.name: quality += 0.25
        if c.description: quality += 0.25
        if c.website: quality += 0.2
        if c.company_size: quality += 0.15
        if c.is_verified: quality += 0.15
        factors["entity_quality"] = quality

        # Evidence score: trust/evidence from context
        trust = context.scoring.trust_score
        factors["evidence_score"] = trust / 100.0 if trust else 0.0

        # Capability match
        cap_score = min(1.0, len(context.capabilities) * 0.2)
        factors["capability_match"] = cap_score

        # Relationship density
        rel_score = min(1.0, len(context.relationships) * 0.15)
        factors["relationship_density"] = rel_score

        # Recency: events recency
        factors["recency"] = 0.5 if context.events else 0.0

        score = ScoreCalculator.weighted_sum(factors, weights)
        explanation = ReasonGenerator.for_visibility(score, factors)
        return {"score": score, "level": self._level(score), "factors": factors, **explanation}
