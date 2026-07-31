"""GEO Intelligence API — Competitive Intelligence with gap analysis and provider recommendations.

Benchmark + Gap Analysis + Action Roadmap + Provider Discovery from gaps.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.company import Company
from app.models.industry import Industry
from app.models.evidence import Evidence
from app.models.capability import Capability
from app.models.relationship import Relationship
from app.models.competitor import Competitor
from app.models.provider import Provider
from app.models.provider_capability import ProviderCapability
from app.models.match_result import MatchResult
from app.models.reputation import Reputation
from app.schemas.competitor import CompetitorCreate, CompetitorResponse
from app.universe.rules import get_rule_engine
from app.universe.registry import get_registry
import uuid, yaml, os

router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence"])


# ── Competitor CRUD ──
@router.get("/competitors")
async def list_competitors(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Competitor))
    return [CompetitorResponse.model_validate(c) for c in r.scalars().all()]


@router.post("/competitors", status_code=201)
async def add_competitor(data: CompetitorCreate, db: AsyncSession = Depends(get_db)):
    c = Competitor(**data.model_dump())
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return CompetitorResponse.model_validate(c)


@router.get("/competitors/config")
async def get_competitor_config():
    path = os.path.join(os.getcwd(), "config", "competitive", "competitors.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Benchmark ──
@router.get("/benchmark/{company_id}")
async def geo_benchmark(company_id: str, db: AsyncSession = Depends(get_db)):
    """GEO Intelligence Loop Phase 1: Industry benchmark and percentile rankings."""
    try:
        uid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(400, "Invalid company ID")

    company = await db.get(Company, uid)
    if not company:
        raise HTTPException(404, "Company not found")

    industry_id = company.industry_id
    result = await db.execute(
        select(Company.id, Company.name, Company.geo_score, Company.company_size)
        .where(Company.industry_id == industry_id)
    )
    peers = result.all()
    scores = [p.geo_score for p in peers if p.geo_score is not None]
    total_peers = len(peers)

    if not scores:
        return {
            "company_id": str(uid),
            "company_name": company.name,
            "industry_id": str(industry_id) if industry_id else None,
            "total_peers": total_peers,
            "message": "No GEO scores available in this industry yet",
            "benchmark": None,
        }

    scores_sorted = sorted(scores, reverse=True)
    avg = round(sum(scores) / len(scores), 1)
    my_score = company.geo_score or 0
    rank = scores_sorted.index(my_score) + 1 if my_score in scores_sorted else len(scores_sorted) + 1
    percentile = round((1 - (rank - 1) / len(scores_sorted)) * 100, 1) if scores_sorted else 0
    top_score = scores_sorted[0]
    median_score = scores_sorted[len(scores_sorted) // 2]
    bottom_score = scores_sorted[-1]

    # Evidence comparison
    ev_result = await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == uid))
    my_evidence = ev_result.scalar() or 0
    all_ev = await db.execute(
        select(func.count(Evidence.id)).where(Evidence.entity_id.in_([p.id for p in peers]))
    )
    total_evidence = all_ev.scalar() or 0
    avg_evidence = round(total_evidence / total_peers, 1) if total_peers > 0 else 0

    # Capability comparison
    cap_result = await db.execute(
        select(func.count(Capability.id)).where(Capability.company_id == uid)
    )
    my_capabilities = cap_result.scalar() or 0
    all_cap = await db.execute(
        select(func.count(Capability.id)).where(Capability.company_id.in_([p.id for p in peers]))
    )
    total_cap = all_cap.scalar() or 0
    avg_capabilities = round(total_cap / total_peers, 1) if total_peers > 0 else 0

    # Relationship comparison
    rel_result = await db.execute(
        select(func.count(Relationship.id)).where(Relationship.source_id == uid)
    )
    my_relationships = rel_result.scalar() or 0
    all_rel = await db.execute(
        select(func.count(Relationship.id)).where(Relationship.source_id.in_([p.id for p in peers]))
    )
    total_rel = all_rel.scalar() or 0
    avg_relationships = round(total_rel / total_peers, 1) if total_peers > 0 else 0

    # Build dimension gaps
    dimensions = [
        {
            "dimension": "GEO Score", "my_value": my_score, "avg_value": avg, "top_value": top_score,
            "gap": round(avg - my_score, 1), "percentile": percentile,
            "status": "leading" if my_score >= avg else "lagging",
        },
        {
            "dimension": "Evidence", "my_value": my_evidence, "avg_value": avg_evidence,
            "gap": round(avg_evidence - my_evidence, 1),
            "status": "sufficient" if my_evidence >= avg_evidence else "insufficient",
            "insight": f"You have {my_evidence} evidence records vs industry avg {avg_evidence}. "
            + ("Strong trust foundation." if my_evidence >= avg_evidence else f"Add {round(avg_evidence - my_evidence)} more records to reach average."),
        },
        {
            "dimension": "Capabilities", "my_value": my_capabilities, "avg_value": avg_capabilities,
            "gap": round(avg_capabilities - my_capabilities, 1),
            "status": "sufficient" if my_capabilities >= avg_capabilities else "insufficient",
            "insight": f"You have {my_capabilities} capabilities vs industry avg {avg_capabilities}. "
            + ("Capability coverage is solid." if my_capabilities >= avg_capabilities else "Expand capability portfolio to stay competitive."),
        },
        {
            "dimension": "Relationships", "my_value": my_relationships, "avg_value": avg_relationships,
            "gap": round(avg_relationships - my_relationships, 1),
            "status": "sufficient" if my_relationships >= avg_relationships else "insufficient",
            "insight": f"You have {my_relationships} relationships vs industry avg {avg_relationships}. "
            + ("Strong ecosystem connection." if my_relationships >= avg_relationships else "Build industry partnerships to improve visibility."),
        },
    ]

    # Roadmap from gaps
    roadmap = []
    lagging_dims = [d for d in dimensions if d.get("status") in ("lagging", "insufficient")]
    lagging_dims.sort(key=lambda d: d["gap"], reverse=True)

    priorities = [
        ("evidence", "P0", "Build trust evidence", "Add certifications, customer cases, third-party validations.", 30),
        ("capability", "P1", "Expand capability coverage", "Identify and fill missing capabilities.", 60),
        ("relationship", "P1", "Strengthen ecosystem connections", "Partner with peers, join GEO alliances.", 90),
        ("geo_score", "P2", "Continuous GEO optimization", "Regular content updates, structured data enhancement.", -1),
    ]

    for dim_key, priority, title, desc, days in priorities:
        matching = [d for d in lagging_dims if dim_key in d["dimension"].lower()]
        if matching or dim_key == "geo_score":
            roadmap.append({
                "priority": priority, "title": title, "description": desc,
                "timeframe_days": days, "target_dimension": dim_key,
                "current_gap": matching[0]["gap"] if matching else None,
            })

    # Universe Rules citation
    engine = get_rule_engine()
    rule_cite = engine.cite("R02", f"Benchmark for {company.name}: score={my_score}, rank={rank}/{len(scores_sorted)}")

    return {
        "company_id": str(uid),
        "company_name": company.name,
        "industry_id": str(industry_id) if industry_id else None,
        "total_peers": total_peers,
        "geo_score": my_score,
        "rank": f"#{rank}/{len(scores_sorted)}" if scores_sorted else "N/A",
        "percentile": percentile,
        "industry_stats": {
            "avg": avg, "median": median_score, "top": top_score, "bottom": bottom_score,
            "scored_count": len(scores_sorted),
        },
        "dimensions": dimensions,
        "roadmap": roadmap,
        "universe_rules": rule_cite,
    }


# ── Gap → Provider Recommendations ──
@router.get("/gaps/{company_id}/providers")
async def providers_for_gaps(company_id: str, db: AsyncSession = Depends(get_db)):
    """Discover candidate providers based on the company's GEO gaps."""
    try:
        uid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(400, "Invalid company ID")

    company = await db.get(Company, uid)
    if not company:
        raise HTTPException(404, "Company not found")

    # Get all active providers with their capabilities
    providers = (await db.execute(
        select(Provider).where(Provider.is_active == True).limit(20)
    )).scalars().all()

    candidates = []
    for p in providers:
        # Get provider capabilities
        caps = (await db.execute(
            select(ProviderCapability).where(ProviderCapability.provider_id == p.id)
        )).scalars().all()

        # Get reputation
        rep = (await db.execute(
            select(Reputation).where(
                Reputation.node_id == p.id, Reputation.node_type == "provider"
            )
        )).scalar_one_or_none()

        pid = str(p.id)[:8]
        candidates.append({
            "provider_id": str(p.id),
            "name": f"Provider {pid}",
            "is_verified": p.is_verified,
            "trust_score": p.trust_score,
            "geo_score": p.geo_score,
            "capabilities_count": len(caps),
            "capabilities": [
                {"capability_id": str(c.capability_id)} for c in caps[:5]
            ],
            "reputation": {
                "total_score": rep.total_score,
                "level": rep.reputation_level if rep and hasattr(rep, "reputation_level") else "N/A",
            } if rep else None,
        })

    engine = get_rule_engine()
    rule_cite = engine.cite("R07", f"Marketplace candidates for {company.name}: {len(candidates)} providers found")

    return {
        "company_id": str(uid),
        "company_name": company.name,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "note": "These are candidates, not recommendations. The enterprise makes its own choice.",
        "universe_rules": rule_cite,
    }


# ── Competitor Deep Compare ──
@router.get("/compare/{company_id}")
async def deep_compare(
    company_id: str,
    competitor_ids: str = Query("", description="Comma-separated competitor IDs"),
    db: AsyncSession = Depends(get_db),
):
    """Deep competitive comparison with evidence gaps and strategic assessment."""
    try:
        uid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(400, "Invalid company ID")

    company = await db.get(Company, uid)
    if not company:
        raise HTTPException(404, "Company not found")

    comp_ids = []
    if competitor_ids:
        for cid in competitor_ids.split(","):
            try:
                comp_ids.append(uuid.UUID(cid.strip()))
            except ValueError:
                pass

    competitors_data = []
    all_ids = [uid] + comp_ids
    for cid in all_ids:
        c = await db.get(Company, cid)
        if not c:
            continue
        ev_count = (await db.execute(
            select(func.count(Evidence.id)).where(Evidence.entity_id == cid)
        )).scalar() or 0
        cap_count = (await db.execute(
            select(func.count(Capability.id)).where(Capability.company_id == cid)
        )).scalar() or 0
        rel_count = (await db.execute(
            select(func.count(Relationship.id)).where(Relationship.source_id == cid)
        )).scalar() or 0
        rep = (await db.execute(
            select(Reputation).where(Reputation.node_id == cid, Reputation.node_type == "company")
        )).scalar_one_or_none()
        competitors_data.append({
            "company_id": str(cid),
            "name": c.name or "Unknown",
            "geo_score": c.geo_score or 0,
            "evidence_count": ev_count,
            "capability_count": cap_count,
            "relationship_count": rel_count,
            "reputation": {
                "total_score": rep.total_score,
                "level": rep.reputation_level if rep and hasattr(rep, "reputation_level") else "N/A",
            } if rep else None,
        })

    # Strategic assessment
    if len(competitors_data) >= 2:
        me = competitors_data[0]
        them = competitors_data[1] if len(competitors_data) > 1 else None
        assessment = {
            "my_score": me["geo_score"],
            "competitor_score": them["geo_score"] if them else None,
            "gap": round(me["geo_score"] - (them["geo_score"] if them else 0), 1) if them else None,
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
        }
        if them:
            if me["evidence_count"] >= them["evidence_count"]:
                assessment["strengths"].append(f"Evidence advantage: +{me['evidence_count'] - them['evidence_count']}")
            else:
                assessment["weaknesses"].append(f"Evidence gap: -{them['evidence_count'] - me['evidence_count']}")
            if me["capability_count"] >= them["capability_count"]:
                assessment["strengths"].append(f"Capability advantage: +{me['capability_count'] - them['capability_count']}")
            else:
                assessment["weaknesses"].append(f"Capability gap: -{them['capability_count'] - me['capability_count']}")
        if len(assessment["weaknesses"]) > 0:
            assessment["opportunities"].append("Address evidence gaps through certification and content creation")
            assessment["opportunities"].append("Expand capability portfolio to close competitive gap")

    engine = get_rule_engine()
    rule_cite = engine.cite("R02", "Competitive comparison: scores + evidence + capability + reputation")

    return {
        "company_id": str(uid),
        "comparison": competitors_data,
        "strategic_assessment": assessment if len(competitors_data) >= 2 else None,
        "universe_rules": rule_cite,
    }
