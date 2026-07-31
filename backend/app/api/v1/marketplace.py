"""GEO Universe Marketplace API — Industry Map Foundation.

Marketplace is the natural business exit of the industry map,
not an add-on. Returns candidate providers (not winners) with
match evidence, capability data, and reputation scores.

All recommendations MUST cite Universe Rules.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.provider import Provider
from app.models.provider_capability import ProviderCapability
from app.models.capability import Capability
from app.models.company import Company
from app.models.industry import Industry
from app.models.evidence import Evidence
from app.models.reputation import Reputation
from app.models.match_result import MatchResult
from app.models.market_demand import MarketDemand
from app.universe.rules import get_rule_engine
from app.universe.registry import get_registry
import uuid

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


# ── Provider List (with real data) ──
@router.get("/providers")
async def list_providers(
    db: AsyncSession = Depends(get_db),
    industry_id: str = Query(None, description="Filter by industry"),
    capability_id: str = Query(None, description="Filter by capability"),
    min_trust: float = Query(None, description="Minimum trust score"),
):
    """List all active providers with their capabilities and reputation."""
    query = select(Provider).where(Provider.is_active == True)

    if min_trust is not None:
        query = query.where(Provider.trust_score >= min_trust)

    providers = (await db.execute(query.limit(30))).scalars().all()

    result = []
    for p in providers:
        # Capabilities
        caps = (await db.execute(
            select(ProviderCapability).where(ProviderCapability.provider_id == p.id)
        )).scalars().all()

        cap_details = []
        for pc in caps[:10]:
            cap = await db.get(Capability, pc.capability_id)
            cap_details.append({
                "capability_id": str(pc.capability_id) if pc.capability_id else None,
                "name": cap.name if cap and cap.name else "Unknown",
                "proficiency": pc.proficiency if hasattr(pc, "proficiency") else None,
            })

        # Reputation
        rep = (await db.execute(
            select(Reputation).where(
                and_(Reputation.node_id == p.id, Reputation.node_type == "provider")
            )
        )).scalar_one_or_none()

        # Evidence
        ev_count = (await db.execute(
            select(func.count(Evidence.id)).where(Evidence.entity_id == p.id)
        )).scalar() or 0

        pid = str(p.id)[:8]
        result.append({
            "provider_id": str(p.id),
            "name": f"Provider {pid}",
            "is_verified": p.is_verified if hasattr(p, "is_verified") else True,
            "trust_score": p.trust_score or 0,
            "geo_score": p.geo_score or 0,
            "capabilities": cap_details,
            "capability_count": len(caps),
            "evidence_count": ev_count,
            "reputation": {
                "total_score": rep.total_score,
                "level": rep.reputation_level if rep and hasattr(rep, "reputation_level") else "N/A",
            } if rep else None,
        })

    engine = get_rule_engine()
    rule_cite = engine.cite("R07", f"Marketplace: {len(result)} active providers listed as candidates")

    return {
        "providers": result,
        "total": len(result),
        "note": "These are candidate providers. Enterprises make their own choice.",
        "universe_rules": rule_cite,
    }


# ── Provider Detail ──
@router.get("/providers/{provider_id}")
async def provider_detail(provider_id: str, db: AsyncSession = Depends(get_db)):
    """Detailed provider profile with capabilities, evidence, and reputation."""
    try:
        uid = uuid.UUID(provider_id)
    except ValueError:
        raise HTTPException(400, "Invalid provider ID")

    provider = await db.get(Provider, uid)
    if not provider:
        raise HTTPException(404, "Provider not found")

    # Capabilities
    caps = (await db.execute(
        select(ProviderCapability).where(ProviderCapability.provider_id == uid)
    )).scalars().all()

    cap_details = []
    for pc in caps:
        cap = await db.get(Capability, pc.capability_id)
        cap_details.append({
            "capability_id": str(pc.capability_id) if pc.capability_id else None,
            "name": cap.name if cap and cap.name else "Unknown",
            "description": cap.description if cap and hasattr(cap, "description") else "",
            "proficiency": pc.proficiency if hasattr(pc, "proficiency") else None,
        })

    # Evidence
    evidence = (await db.execute(
        select(Evidence).where(Evidence.entity_id == uid).limit(10)
    )).scalars().all()

    ev_list = [
        {
            "id": str(ev.id),
            "evidence_type": ev.evidence_type if hasattr(ev, "evidence_type") else "general",
            "title": ev.title if hasattr(ev, "title") else "",
            "url": ev.url if hasattr(ev, "url") else "",
        }
        for ev in evidence
    ]

    # Reputation
    rep = (await db.execute(
        select(Reputation).where(
            and_(Reputation.node_id == uid, Reputation.node_type == "provider")
        )
    )).scalar_one_or_none()

    # Match history
    matches = (await db.execute(
        select(MatchResult).where(MatchResult.provider_id == uid).limit(10)
    )).scalars().all()

    match_list = [
        {
            "id": str(m.id),
            "score": m.match_score if hasattr(m, "match_score") else 0,
            "demand_id": str(m.demand_id) if hasattr(m, "demand_id") else None,
        }
        for m in matches
    ]

    pid = str(provider.id)[:8]
    return {
        "provider": {
            "id": str(uid),
            "name": f"Provider {pid}",
            "is_verified": provider.is_verified if hasattr(provider, "is_verified") else True,
            "trust_score": provider.trust_score or 0,
            "geo_score": provider.geo_score or 0,
            "description": provider.description if hasattr(provider, "description") else "",
            "capabilities": cap_details,
            "evidence": ev_list,
            "reputation": {
                "total_score": rep.total_score,
                "level": rep.reputation_level if rep and hasattr(rep, "reputation_level") else "N/A",
                "industry_rank": rep.industry_rank if rep and hasattr(rep, "industry_rank") else 0,
            } if rep else None,
            "match_history": match_list,
        },
    }


# ── Demands ──
@router.get("/demands")
async def list_demands(
    db: AsyncSession = Depends(get_db),
    industry_id: str = Query(None),
):
    """List market demands, optionally filtered by industry."""
    query = select(MarketDemand)
    if industry_id:
        query = query.where(MarketDemand.industry_id == industry_id)

    demands = (await db.execute(query.limit(20))).scalars().all()

    result = []
    for d in demands:
        company = await db.get(Company, d.company_id) if hasattr(d, "company_id") and d.company_id else None
        result.append({
            "id": str(d.id),
            "title": d.title if hasattr(d, "title") else "Demand",
            "description": d.description if hasattr(d, "description") else "",
            "status": d.status if hasattr(d, "status") else "open",
            "company_id": str(d.company_id) if hasattr(d, "company_id") and d.company_id else None,
            "company_name": company.name if company else "Unknown",
            "created_at": str(d.created_at) if hasattr(d, "created_at") else "",
        })

    return {"demands": result, "total": len(result)}


# ── Demand → Candidate Providers ──
@router.get("/demands/{demand_id}/candidates")
async def demand_candidates(demand_id: str, db: AsyncSession = Depends(get_db)):
    """For a given demand, return matching candidate providers."""
    try:
        uid = uuid.UUID(demand_id)
    except ValueError:
        raise HTTPException(400, "Invalid demand ID")

    demand = await db.get(MarketDemand, uid)
    if not demand:
        raise HTTPException(404, "Demand not found")

    # Find providers matching this demand
    matches = (await db.execute(
        select(MatchResult).where(MatchResult.demand_id == uid).order_by(
            MatchResult.match_score.desc() if hasattr(MatchResult, "match_score") else MatchResult.id
        ).limit(10)
    )).scalars().all()

    candidates = []
    for m in matches:
        provider = await db.get(Provider, m.provider_id) if hasattr(m, "provider_id") and m.provider_id else None
        if provider:
            pid = str(provider.id)[:8]
            rep = (await db.execute(
                select(Reputation).where(
                    and_(Reputation.node_id == provider.id, Reputation.node_type == "provider")
                )
            )).scalar_one_or_none()
            candidates.append({
                "match_id": str(m.id),
                "provider_id": str(provider.id),
                "name": f"Provider {pid}",
                "match_score": m.match_score if hasattr(m, "match_score") else 0,
                "match_dimensions": m.match_dimensions if hasattr(m, "match_dimensions") else {},
                "trust_score": provider.trust_score or 0,
                "reputation_level": rep.reputation_level if rep and hasattr(rep, "reputation_level") else "N/A",
            })

    engine = get_rule_engine()
    rule_cite = engine.cite("R02", f"Demand matching: {len(candidates)} candidate providers")

    return {
        "demand_id": str(uid),
        "candidates": candidates,
        "total": len(candidates),
        "note": "Candidates are listed by match score. Enterprise makes its own selection.",
        "universe_rules": rule_cite,
    }
