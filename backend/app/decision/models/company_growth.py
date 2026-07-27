from typing import Any
from app.decision.models.base import DecisionModel
from app.decision.scoring.calculator import ScoreCalculator
from app.decision.explanation.reason_generator import ReasonGenerator
from app.context.schemas.context_schema import CompanyContext


class CompanyGrowthScore(DecisionModel):
    async def calculate(self, context: CompanyContext) -> dict:
        visibility = getattr(context.scoring, "geo_score", 0) / 100.0
        trust = context.scoring.trust_score / 100.0
        cap_breadth = min(1.0, len(context.capabilities) * 0.15)
        event_momentum = min(1.0, len(context.events) * 0.2)
        rel_network = min(1.0, len(context.relationships) * 0.1)

        score = ScoreCalculator.weighted_sum(
            {"visibility": visibility, "trust": trust, "capabilities": cap_breadth,
             "events": event_momentum, "relationships": rel_network},
            {"visibility": 0.25, "trust": 0.25, "capabilities": 0.20, "events": 0.15, "relationships": 0.15}
        )
        explanation = ReasonGenerator.for_growth(score, {})
        return {"score": score, "level": self._level(score), **explanation}


class CompetitivePosition(DecisionModel):
    async def calculate(self, context: CompanyContext) -> dict:
        visibility = context.scoring.geo_score / 100.0 if context.scoring.geo_score else 0.0
        trust = context.scoring.trust_score / 100.0
        rel_size = min(1.0, len(context.relationships) * 0.12)
        score = ScoreCalculator.weighted_sum(
            {"visibility": visibility, "trust": trust, "network": rel_size},
            {"visibility": 0.40, "trust": 0.35, "network": 0.25}
        )
        return {"score": score, "level": self._level(score),
                "reasons": ["Visibility: " + ("strong" if visibility > 0.5 else "needs improvement"),
                            "Trust: " + ("established" if trust > 0.5 else "developing")],
                "actions": ["Improve evidence base" if trust < 0.5 else "Maintain current position"]}


class GEORoadmap(DecisionModel):
    async def calculate(self, context: CompanyContext) -> dict:
        visibility = context.scoring.geo_score or 0
        trust = context.scoring.trust_score
        cap_count = len(context.capabilities)
        ev_count = len(context.evidence)
        actions = []
        if cap_count < 3:
            actions.append("Add core capabilities (minimum 3)")
        if ev_count < 2:
            actions.append("Provide verifiable evidence for each capability")
        if visibility < 50:
            actions.append("Improve entity completeness: add description, website, case studies")
        if trust < 40:
            actions.append("Build trust signals: collect certifications, customer reviews")
        actions.append("Monitor GEO score changes weekly")
        return {"score": visibility, "level": self._level(visibility),
                "actions": actions[:5], "reasons": ["Roadmap generated from score breakdown"]}


class ContentStrategy(DecisionModel):
    async def calculate(self, context: CompanyContext) -> dict:
        c = context.company
        gaps = []
        if not c.description: gaps.append("Write a detailed company description")
        if not c.website: gaps.append("Add official website")
        if len(context.capabilities) < 2: gaps.append("Document at least 2 core capabilities")
        if len(context.evidence) < 1: gaps.append("Add evidence: case studies, certifications")
        score = max(0, 100 - len(gaps) * 20)
        return {"score": score, "level": self._level(score),
                "actions": gaps + ["Review and update content quarterly"],
                "reasons": ["Content gaps identified: " + str(len(gaps))]}


class MarketConnection(DecisionModel):
    async def calculate(self, context: CompanyContext) -> dict:
        rel_count = len(context.relationships)
        score = min(100, rel_count * 15)
        return {"score": score, "level": self._level(score),
                "reasons": [f"Current relationships: {rel_count}"],
                "actions": ["Explore partnership opportunities in complementary industries",
                            "Connect with industry platforms and associations"]}
