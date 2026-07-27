from app.decision.models.base import DecisionModel
from app.context.schemas.context_schema import CapabilityContext


class CapabilityMatchScore(DecisionModel):
    async def calculate(self, context: CapabilityContext) -> dict:
        cap = context.capability
        level_score = cap.level / 4.0
        provider_score = 1.0 if context.providers else 0.0
        rel_score = min(1.0, len(context.relationships) * 0.2)
        ev_score = min(1.0, len(context.evidence) * 0.25)
        score = (level_score * 0.35 + provider_score * 0.30 + rel_score * 0.20 + ev_score * 0.15) * 100
        return {"score": round(score, 1), "level": self._level(score),
                "reasons": [f"Capability level: L{cap.level}/L4",
                            f"Providers available: {len(context.providers)}"],
                "actions": ["Gather more evidence" if not context.evidence else "Maintain capability documentation"]}
