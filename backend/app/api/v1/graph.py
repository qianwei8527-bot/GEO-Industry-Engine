"""GEO Universe Graph API — Layer 2 Graph with full five-layer data.

Returns nodes + edges for ecosystem visualization (Cytoscape.js-ready),
including competitors, growth stages, reputations, and geo_events.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.industry import Industry
from app.models.company import Company
from app.models.provider import Provider
from app.models.relationship import Relationship
from app.models.capability import Capability
from app.models.provider_capability import ProviderCapability
from app.models.competitor import Competitor
from app.models.growth_stage import GrowthStage
from app.models.reputation import Reputation
from app.models.geo_event import GeoEvent
from app.models.evidence import Evidence
from app.models.trust import Trust
from app.universe.rules import get_rule_engine
from app.universe.registry import get_registry
from app.universe.node import is_valid_node_type

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


def score_color(score: float) -> str:
    if score >= 70:
        return "green"
    if score >= 40:
        return "amber"
    return "red"


def size_label(score: float) -> str:
    if score >= 70:
        return "large"
    if score >= 40:
        return "medium"
    return "small"


@router.get("/ecosystem/{industry_id}")
async def ecosystem_graph(industry_id: str, db: AsyncSession = Depends(get_db)):
    """Return full ecosystem graph for an industry with five-layer data.

    Returns Cytoscape.js-ready nodes + edges including:
    - Layer 1: Company/Provider/Capability nodes
    - Layer 2: Relationship/Competitor/ProviderCapability edges
    - Layer 3: Recent geo_events
    - Layer 4: Growth stages + Value chains
    - Layer 5: Reputation scores
    """
    try:
        uid = uuid.UUID(industry_id)
    except ValueError:
        raise HTTPException(400, "Invalid industry ID")

    industry = (await db.execute(
        select(Industry).where(Industry.id == uid)
    )).scalar_one_or_none()
    if not industry:
        raise HTTPException(404, "Industry not found")

    # ── Layer 1: Nodes ──
    companies = (await db.execute(
        select(Company).where(Company.industry_id == str(uid)).limit(30)
    )).scalars().all()

    providers = (await db.execute(
        select(Provider).where(Provider.is_active == True).limit(20)
    )).scalars().all()

    capabilities = (await db.execute(select(Capability).limit(30))).scalars().all()

    nodes = []

    # Industry node
    nodes.append({
        "id": f"ind_{industry.id}",
        "type": "industry",
        "name": industry.name,
        "code": industry.code,
        "layer": "node",
        "group": "industry",
    })

    # Company nodes
    for c in companies:
        gs = c.geo_score or 0
        nodes.append({
            "id": f"comp_{c.id}",
            "type": "company",
            "name": c.name or "Unknown",
            "geo_score": gs,
            "entity_type": c.entity_type,
            "layer": "node",
            "group": "company",
            "size": size_label(gs),
            "score_color": score_color(gs),
        })

    # Provider nodes
    for p in providers:
        pid_short = str(p.id)[:8]
        nodes.append({
            "id": f"prov_{p.id}",
            "type": "provider",
            "name": f"Provider {pid_short}",
            "trust_score": p.trust_score,
            "geo_score": p.geo_score,
            "is_verified": p.is_verified,
            "layer": "node",
            "group": "provider",
            "size": size_label(p.geo_score or 0),
            "score_color": score_color(p.geo_score or 0),
        })

    # Capability nodes
    for cap in capabilities:
        nodes.append({
            "id": f"cap_{cap.id}",
            "type": "capability",
            "name": cap.name or f"Capability {str(cap.id)[:8]}",
            "layer": "node",
            "group": "capability",
        })

    # ── Layer 2: Edges ──
    edges = []

    # Company → Industry
    for c in companies:
        edges.append({
            "id": f"e_ci_{c.id}",
            "source": f"comp_{c.id}",
            "target": f"ind_{industry.id}",
            "relation": "belongs_to",
            "layer": "graph",
            "group": "membership",
        })

    # Relationships
    relationships = (await db.execute(select(Relationship).limit(80))).scalars().all()
    for r in relationships:
        if r.source_id and r.target_id:
            edges.append({
                "id": f"e_rel_{r.id}",
                "source": f"comp_{r.source_id}",
                "target": f"comp_{r.target_id}",
                "relation": r.relation_type or "related",
                "layer": "graph",
                "group": "relationship",
                "weight": r.weight or 1.0,
            })

    # Provider → Capability
    prov_caps = (await db.execute(select(ProviderCapability).limit(30))).scalars().all()
    for pc in prov_caps:
        edges.append({
            "id": f"e_pc_{pc.provider_id}_{pc.capability_id}",
            "source": f"prov_{pc.provider_id}",
            "target": f"cap_{pc.capability_id}",
            "relation": "has_capability",
            "layer": "graph",
            "group": "capability",
        })

    # Competitors → Graph edges (Sprint 4.0-C)
    company_ids = [str(c.id) for c in companies]
    competitors = (await db.execute(
        select(Competitor).where(Competitor.company_id.in_(company_ids))
    )).scalars().all()
    for comp in competitors:
        edges.append({
            "id": f"e_comp_{comp.id}",
            "source": f"comp_{comp.company_id}",
            "target": f"comp_{comp.competitor_company_id}"
            if hasattr(comp, "competitor_company_id") and comp.competitor_company_id
            else f"comp_{comp.id}",
            "relation": "competitor",
            "layer": "graph",
            "group": "competition",
            "geo_score_diff": comp.geo_score_diff if hasattr(comp, "geo_score_diff") else None,
        })

    # Company → Capability (if any company has capabilities linked)
    for c in companies:
        caps = (await db.execute(
            select(Capability).where(Capability.company_id == c.id)
        )).scalars().all()
        for cap in caps:
            edges.append({
                "id": f"e_cc_{c.id}_{cap.id}",
                "source": f"comp_{c.id}",
                "target": f"cap_{cap.id}",
                "relation": "has_capability",
                "layer": "graph",
                "group": "capability",
            })

    # ── Layer 3: Dynamic Events ──
    geo_events = (await db.execute(
        select(GeoEvent).order_by(GeoEvent.created_at.desc()).limit(20)
    )).scalars().all()
    events_layer = {
        "count": len(geo_events),
        "recent": [
            {
                "id": str(ge.id),
                "event_type": ge.event_type if hasattr(ge, "event_type") else "unknown",
                "impact_score": ge.impact_score if hasattr(ge, "impact_score") else 0,
                "description": ge.description if hasattr(ge, "description") else "",
                "created_at": str(ge.created_at) if hasattr(ge, "created_at") else "",
            }
            for ge in geo_events[:5]
        ],
    }

    # ── Layer 4: Growth Stages ──
    growth_data = []
    for c in companies[:10]:
        gs = (await db.execute(
            select(GrowthStage).where(
                and_(GrowthStage.node_id == c.id, GrowthStage.node_type == "company")
            )
        )).scalar_one_or_none()
        if gs:
            growth_data.append({
                "node_id": f"comp_{c.id}",
                "stage": gs.current_stage if hasattr(gs, "current_stage") else "unknown",
                "level": gs.stage_level if hasattr(gs, "stage_level") else 1,
                "progress": gs.stage_progress if hasattr(gs, "stage_progress") else 0,
            })

    # ── Layer 5: Reputation ──
    reputation_data = []
    for c in companies[:10]:
        rep = (await db.execute(
            select(Reputation).where(
                and_(Reputation.node_id == c.id, Reputation.node_type == "company")
            )
        )).scalar_one_or_none()
        if rep:
            reputation_data.append({
                "node_id": f"comp_{c.id}",
                "total_score": rep.total_score,
                "level": rep.reputation_level if hasattr(rep, "reputation_level") else "N/A",
                "industry_rank": rep.industry_rank if hasattr(rep, "industry_rank") else 0,
            })

    # Universe Rules citation
    engine = get_rule_engine()
    rule_citation = engine.cite("R05", f"Ecosystem view for industry '{industry.name}'")
    rule_citation += "\n" + engine.cite("R08", "Nodes maintain unified state across all five views")

    return {
        "universe": {
            "industry": {"id": str(industry.id), "name": industry.name, "code": industry.code},
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "groups": {
                "company": len([n for n in nodes if n["group"] == "company"]),
                "provider": len([n for n in nodes if n["group"] == "provider"]),
                "capability": len([n for n in nodes if n["group"] == "capability"]),
            },
        },
        "layer_3_dynamic": events_layer,
        "layer_4_evolution": {"growth": growth_data},
        "layer_5_reputation": reputation_data,
        "universe_rules": rule_citation,
    }


@router.get("/overview")
async def universe_overview(db: AsyncSession = Depends(get_db)):
    """Return a lightweight Universe overview: stats, layer status, industry list."""
    industries = (await db.execute(select(Industry).limit(10))).scalars().all()
    cc = (await db.execute(select(func.count(Company.id)))).scalar() or 0
    pc = (await db.execute(select(func.count(Provider.id)))).scalar() or 0
    rc = (await db.execute(select(func.count(Relationship.id)))).scalar() or 0
    ec = (await db.execute(select(func.count(Evidence.id)))).scalar() or 0
    gc = (await db.execute(select(func.count(GeoEvent.id)))).scalar() or 0
    gsc = (await db.execute(select(func.count(GrowthStage.id)))).scalar() or 0
    repc = (await db.execute(select(func.count(Reputation.id)))).scalar() or 0

    result = []
    for ind in industries:
        cnt = (await db.execute(
            select(func.count(Company.id)).where(Company.industry_id == str(ind.id))
        )).scalar() or 0
        result.append({
            "id": str(ind.id),
            "name": ind.name,
            "code": ind.code,
            "company_count": cnt,
        })

    return {
        "universe_stats": {
            "industries": len(industries),
            "companies": cc,
            "providers": pc,
            "relationships": rc,
            "evidence_records": ec,
            "geo_events": gc,
            "growth_stages_populated": gsc,
            "reputations_scored": repc,
        },
        "industries": result,
        "layers": {
            "node": "active" if cc > 0 else "empty",
            "graph": "active" if rc > 0 else "empty",
            "dynamic": "active" if gc > 0 else "initializing",
            "evolution": "active" if gsc > 0 else "initializing",
            "intelligence": "active" if repc > 0 else "initializing",
            "rules": "active",
        },
    }


@router.get("/nodes/{node_type}/{node_id}")
async def node_detail(node_type: str, node_id: str, db: AsyncSession = Depends(get_db)):
    """Get detail for a specific node including its GEO Passport data."""
    try:
        uid = uuid.UUID(node_id)
    except ValueError:
        raise HTTPException(400, "Invalid node ID")

    data = {"node_id": str(uid), "node_type": node_type, "passport": {}}

    if node_type == "company":
        company = await db.get(Company, uid)
        if not company:
            raise HTTPException(404, "Company not found")

        # Evidence count
        ev_count = (await db.execute(
            select(func.count(Evidence.id)).where(Evidence.entity_id == uid)
        )).scalar() or 0

        # Relationships count
        rel_count = (await db.execute(
            select(func.count(Relationship.id)).where(Relationship.source_id == uid)
        )).scalar() or 0

        # Growth stage
        gs = (await db.execute(
            select(GrowthStage).where(
                and_(GrowthStage.node_id == uid, GrowthStage.node_type == "company")
            )
        )).scalar_one_or_none()

        # Reputation
        rep = (await db.execute(
            select(Reputation).where(
                and_(Reputation.node_id == uid, Reputation.node_type == "company")
            )
        )).scalar_one_or_none()

        # Competitors
        comps = (await db.execute(
            select(Competitor).where(Competitor.company_id == str(uid))
        )).scalars().all()

        data["passport"] = {
            "name": company.name,
            "industry_id": company.industry_id,
            "geo_score": company.geo_score,
            "entity_type": company.entity_type,
            "evidence_count": ev_count,
            "relationship_count": rel_count,
            "growth_stage": {
                "stage": gs.current_stage if gs and hasattr(gs, "current_stage") else "unknown",
                "level": gs.stage_level if gs and hasattr(gs, "stage_level") else 1,
                "progress": gs.stage_progress if gs and hasattr(gs, "stage_progress") else 0,
            } if gs else None,
            "reputation": {
                "total_score": rep.total_score,
                "level": rep.reputation_level if rep and hasattr(rep, "reputation_level") else "N/A",
                "rank": rep.industry_rank if rep and hasattr(rep, "industry_rank") else 0,
            } if rep else None,
            "competitors": [
                {"id": str(c.id), "name": c.competitor_name if hasattr(c, "competitor_name") else "Unknown"}
                for c in comps[:5]
            ],
        }

    elif node_type == "provider":
        provider = await db.get(Provider, uid)
        if not provider:
            raise HTTPException(404, "Provider not found")

        caps = (await db.execute(
            select(ProviderCapability).where(ProviderCapability.provider_id == uid)
        )).scalars().all()

        rep = (await db.execute(
            select(Reputation).where(
                and_(Reputation.node_id == uid, Reputation.node_type == "provider")
            )
        )).scalar_one_or_none()

        data["passport"] = {
            "name": f"Provider {str(provider.id)[:8]}",
            "is_verified": provider.is_verified,
            "trust_score": provider.trust_score,
            "geo_score": provider.geo_score,
            "capability_count": len(caps),
            "reputation": {
                "total_score": rep.total_score,
                "level": rep.reputation_level if rep and hasattr(rep, "reputation_level") else "N/A",
            } if rep else None,
        }

    return data

# ── View-Specific Graph Endpoints ──
# 五View独立API：每个View返回真正差异化的图数据

@router.get("/business/{industry_id}")
async def business_graph(industry_id: str, db: AsyncSession = Depends(get_db)):
    """Business View: GEO score tiering + value chain orientation."""
    try:
        uid = uuid.UUID(industry_id)
    except ValueError:
        raise HTTPException(400, "Invalid industry ID")

    companies = (await db.execute(
        select(Company).where(Company.industry_id == str(uid)).limit(30)
    )).scalars().all()

    providers = (await db.execute(
        select(Provider).where(Provider.is_active == True).limit(20)
    )).scalars().all()

    nodes = []
    for c in companies:
        gs = c.geo_score or 0
        nodes.append({
            "id": f"comp_{c.id}", "type": "company", "name": c.name or "Unknown",
            "geo_score": gs, "tier": "high" if gs >= 60 else ("mid" if gs >= 30 else "low"),
            "size": "large" if gs >= 60 else ("medium" if gs >= 30 else "small"),
            "group": "company",
        })

    for p in providers:
        gs = p.geo_score or 0
        nodes.append({
            "id": f"prov_{p.id}", "type": "provider",
            "name": f"Provider {str(p.id)[:8]}",
            "geo_score": gs, "tier": "high" if gs >= 60 else ("mid" if gs >= 30 else "low"),
            "is_verified": p.is_verified, "group": "provider",
        })

    edges = []
    pcs = (await db.execute(select(ProviderCapability).limit(50))).scalars().all()
    for pc in pcs:
        edges.append({
            "id": f"e_vc_{pc.id}", "source": f"comp_{pc.company_id}", "target": f"prov_{pc.provider_id}",
            "relation": "value_flow", "group": "value_chain",
        })

    rels = (await db.execute(select(Relationship).limit(60))).scalars().all()
    for r in rels:
        if r.source_id and r.target_id:
            edges.append({
                "id": f"e_rel_{r.id}", "source": f"comp_{r.source_id}", "target": f"comp_{r.target_id}",
                "relation": r.relation_type or "related", "group": "relationship",
            })

    return {"view": "business", "nodes": nodes, "edges": edges}


@router.get("/growth/{industry_id}")
async def growth_graph(industry_id: str, db: AsyncSession = Depends(get_db)):
    """Growth View: Growth stages + progression paths."""
    try:
        uid = uuid.UUID(industry_id)
    except ValueError:
        raise HTTPException(400, "Invalid industry ID")

    companies = (await db.execute(
        select(Company).where(Company.industry_id == str(uid)).limit(30)
    )).scalars().all()

    nodes = []
    for c in companies:
        gs = c.geo_score or 0
        stage = "Established" if gs >= 70 else ("Active" if gs >= 35 else "Entry")
        nodes.append({
            "id": f"comp_{c.id}", "type": "company", "name": c.name or "Unknown",
            "geo_score": gs, "growth_stage": stage, "group": "company",
        })

    gss = (await db.execute(select(GrowthStage).limit(30))).scalars().all()
    for g in gss:
        stage_name = getattr(g, "current_stage", None)
        if stage_name and hasattr(g, "node_id"):
            nodes.append({
                "id": f"gs_{g.id}", "type": "growth_stage", "name": stage_name, "group": "growth_stage",
            })

    edges = []
    for g in gss:
        if hasattr(g, "node_id"):
            edges.append({
                "id": f"e_gs_{g.id}", "source": f"comp_{g.node_id}", "target": f"gs_{g.id}",
                "relation": "growth", "group": "progression",
            })

    return {"view": "growth", "nodes": nodes, "edges": edges}


@router.get("/distribution/{industry_id}")
async def distribution_graph(industry_id: str, db: AsyncSession = Depends(get_db)):
    """Distribution View: Regional clustering."""
    try:
        uid = uuid.UUID(industry_id)
    except ValueError:
        raise HTTPException(400, "Invalid industry ID")

    companies = (await db.execute(
        select(Company).where(Company.industry_id == str(uid)).limit(30)
    )).scalars().all()

    nodes = []
    for c in companies:
        gs = c.geo_score or 0
        nodes.append({
            "id": f"comp_{c.id}", "type": "company", "name": c.name or "Unknown",
            "geo_score": gs, "group": "company",
            "density": "high" if gs >= 60 else ("medium" if gs >= 30 else "low"),
        })

    edges = []
    rels = (await db.execute(select(Relationship).limit(50))).scalars().all()
    for r in rels:
        if r.source_id and r.target_id:
            edges.append({
                "id": f"e_loc_{r.id}", "source": f"comp_{r.source_id}", "target": f"comp_{r.target_id}",
                "relation": "regional", "group": "regional",
            })

    return {"view": "distribution", "nodes": nodes, "edges": edges}


@router.get("/future/{industry_id}")
async def future_graph(industry_id: str, db: AsyncSession = Depends(get_db)):
    """Future View: Trend signals + emerging patterns."""
    try:
        uid = uuid.UUID(industry_id)
    except ValueError:
        raise HTTPException(400, "Invalid industry ID")

    companies = (await db.execute(
        select(Company).where(Company.industry_id == str(uid)).limit(30)
    )).scalars().all()

    events = (await db.execute(
        select(GeoEvent).order_by(GeoEvent.created_at.desc()).limit(20)
    )).scalars().all()

    nodes = []
    for c in companies:
        gs = c.geo_score or 0
        has_event = any(
            hasattr(e, "affected_node_id") and str(e.affected_node_id) == str(c.id)
            for e in events
        ) if events else False
        nodes.append({
            "id": f"comp_{c.id}", "type": "company", "name": c.name or "Unknown",
            "geo_score": gs, "trending": has_event, "signal": "trending" if has_event else "stable",
            "group": "company",
        })

    edges = []
    for e in events:
        if hasattr(e, "affected_node_id"):
            edges.append({
                "id": f"e_future_{e.id}", "source": f"comp_{e.affected_node_id}",
                "target": f"comp_{e.affected_node_id}",
                "relation": getattr(e, "event_type", "signal"), "group": "future_signal",
            })

    return {"view": "future", "nodes": nodes, "edges": edges}
