from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.market_demand import MarketDemand
from app.models.provider import Provider
from app.models.provider_capability import ProviderCapability
from app.models.capability import Capability
from app.models.industry import Industry
from app.models.match_result import MatchResult
from app.core.config_loader import config_loader
import uuid

class GEOMatchingEngine:
    def __init__(self):
        self.config = config_loader._load_yaml("matching/match_weights.yaml")

    async def match(self, demand_id: str, db: AsyncSession, top_k: int = 5):
        demand = (await db.execute(select(MarketDemand).where(MarketDemand.id == demand_id))).scalar_one_or_none()
        if not demand:
            raise ValueError(f"Demand {demand_id} not found")

        candidates = await self._retrieve_candidates(demand, db)
        if not candidates:
            return {"demand_id": demand_id, "matches": [], "generated_at": None}

        weights = self._get_weights()
        scored = []
        for provider in candidates:
            score_detail, total, reasons = await self._score(demand, provider, weights, db)
            scored.append((provider, total, score_detail, reasons))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_k]

        results = []
        for rank, (provider, score, detail, reasons) in enumerate(top, 1):
            mr = MatchResult(
                id=uuid.uuid4(), demand_id=demand_id, provider_id=provider.id,
                score=round(score, 4), rank=rank, reasons=reasons,
                scores_detail=detail, status="generated"
            )
            db.add(mr)
            results.append({
                "provider_id": str(provider.id),
                "score": round(score, 4),
                "level": "strong" if score >= 0.75 else "moderate" if score >= 0.5 else "weak",
                "reasons": reasons,
                "scores_detail": detail,
            })

        if results:
            demand.matched_providers = [r["provider_id"] for r in results]
        await db.commit()
        return {"demand_id": demand_id, "matches": results, "generated_at": demand.updated_at.isoformat()}

    async def _retrieve_candidates(self, demand, db):
        stmt = select(Provider).where(Provider.is_active == True)
        if demand.industry_id:
            pass  # filter handled in _score via industry_fit
        r = await db.execute(stmt)
        return r.scalars().all()

    def _get_weights(self):
        w = self.config.get("weights", {})
        return {
            "capability_overlap": w.get("capability_overlap", 0.25),
            "industry_fit": w.get("industry_fit", 0.20),
            "trust_score": w.get("trust_score", 0.20),
            "geo_score": w.get("geo_score", 0.15),
            "certification": w.get("certification", 0.10),
            "budget_fit": w.get("budget_fit", 0.10),
        }

    async def _score(self, demand, provider, weights, db):
        detail = {}
        reasons = []

        # 1. Capability overlap
        cap_overlap = await self._calc_capability_overlap(demand, provider, db)
        detail["capability_overlap"] = round(cap_overlap, 4)
        if cap_overlap > 0.5:
            reasons.append(f"能力覆盖度 {cap_overlap:.0%}")

        # 2. Industry fit
        if demand.industry_id:
            industry_fit = await self._calc_industry_fit(demand.industry_id, provider, db)
        else:
            industry_fit = 0.5
        detail["industry_fit"] = round(industry_fit, 4)
        if industry_fit > 0.6:
            reasons.append("行业匹配度高")

        # 3. Trust score
        trust = provider.trust_score / 100.0 if provider.trust_score else 0.0
        detail["trust_score"] = round(trust, 4)
        if trust > 0.7:
            reasons.append("高可信度服务商")

        # 4. GEO score
        geo = provider.geo_score / 100.0 if provider.geo_score else 0.0
        detail["geo_score"] = round(geo, 4)

        # 5. Certification
        cert_bonus = 0.8 if provider.is_verified else 0.3
        detail["certification"] = round(cert_bonus, 4)
        if provider.is_verified:
            reasons.append("已认证服务商")

        # 6. Budget fit
        budget_fit = self._calc_budget_fit(demand, provider)
        detail["budget_fit"] = round(budget_fit, 4)
        if budget_fit > 0.7:
            reasons.append("预算匹配")

        total = sum(weights[k] * detail[k] for k in weights)
        return detail, total, reasons

    async def _calc_capability_overlap(self, demand, provider, db):
        prov_caps = (await db.execute(
            select(ProviderCapability).where(ProviderCapability.provider_id == provider.id)
        )).scalars().all()
        if not prov_caps:
            return 0.0
        capability_ids = [pc.capability_id for pc in prov_caps]
        caps = (await db.execute(
            select(Capability).where(Capability.id.in_(capability_ids))
        )).scalars().all()
        if not caps:
            return 0.0
        demand_reqs = demand.requirements or {}
        keywords = demand_reqs.get("keywords", []) + [demand.title, demand.description or ""]
        matched = 0
        for cap in caps:
            cap_text = (cap.name or "") + " " + (cap.description or "")
            for kw in keywords:
                if kw.lower() in cap_text.lower():
                    matched += 1
                    break
        return min(matched / max(len(caps), 1), 1.0)

    async def _calc_industry_fit(self, industry_id, provider, db):
        prov_caps = (await db.execute(
            select(ProviderCapability).where(ProviderCapability.provider_id == provider.id)
        )).scalars().all()
        if not prov_caps:
            return 0.3
        return 1.0  # placeholder: full industry context needs richer provider-industry relationship

    def _calc_budget_fit(self, demand, provider):
        pricing = provider.pricing_model or {}
        if not demand.budget_min or not pricing:
            return 0.5
        p_min = pricing.get("range_min") or pricing.get("rate")
        if p_min and demand.budget_min <= p_min * 2:
            return 0.8
        return 0.4

    def reload_weights(self):
        self.config = config_loader._load_yaml("matching/match_weights.yaml")
