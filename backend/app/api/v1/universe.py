"""Universe Rules API — Layer 0 Foundation + Intelligence Panel.

Provides Universe Rules for Agent citation, decision validation,
map trigger inspection, and the Intelligence Panel data aggregation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.universe.rules import get_rule_engine
from app.universe.registry import get_registry
from app.universe.node import is_valid_node_type, get_node_type_label
from app.universe.runtime import get_runtime
from app.universe.plugin_registry import get_plugin_registry
from app.domain.event_store import get_event_store, UniverseEvent
from app.universe.ai_provider import get_ai_provider_registry, ChatMessage, ChatCompletionRequest
from app.universe.world_model import get_world_model, LivingWorldModel
from app.universe.position_engine import get_position_engine
from app.universe.memory_engine import get_memory_engine
from app.universe.capability_engine import get_capability_registry, CapabilityRegistry
from app.universe.context_engine import get_context_engine, ContextEngine, NodeContext
from app.universe.decision_engine import get_decision_engine, DecisionEngine, CandidatePath, DecisionReport
from app.universe.possibility_engine import get_possibility_engine, PossibilityEngine, PossibilityGraph, DecisionMemory
from app.universe.future_registry import get_future_registry, FutureStateRegistry, FutureStateTemplate
from app.universe.connection_engine import get_connection_engine, FutureConnectionEngine, ConnectionReport
from app.universe.reputation_engine import get_reputation_engine
from app.universe.relationship_engine import get_relationship_engine, RelationshipEngine, Relationship, RelationshipEvent, RelationshipReputation
from app.models.company import Company
from app.models.provider import Provider
from app.models.industry import Industry
from app.models.evidence import Evidence
from app.models.capability import Capability
from app.models.relationship import Relationship
from app.models.competitor import Competitor
from app.models.growth_stage import GrowthStage
from app.models.reputation import Reputation
from app.models.geo_event import GeoEvent
from app.models.provider_capability import ProviderCapability
import uuid

router = APIRouter(prefix="/api/v1/universe", tags=["universe"])


# ── Universe Rules ──

@router.get("/rules")
async def list_all_rules(
    category: str = Query(None), layer: str = Query(None), trigger: str = Query(None),
):
    engine = get_rule_engine()
    if trigger:
        rules = engine.rules.get_rules_triggered_by(trigger)
    elif layer:
        rules = engine.rules.get_rules_affecting_layer(layer)
    elif category:
        rules = engine.rules.get_rules_by_category(category)
    else:
        rules = engine.rules.rules
    return {
        "count": len(rules),
        "rules": [{"id": r["id"], "name": r["name"], "category": r.get("category", ""),
                    "description": r.get("description", "")} for r in rules],
    }


@router.get("/rules/{rule_id}")
async def get_rule(rule_id: str):
    engine = get_rule_engine()
    rule = engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(404, f"Rule {rule_id} not found")
    return {"rule": rule}


@router.get("/categories")
async def list_categories():
    engine = get_rule_engine()
    return {"categories": engine.get_categories()}


@router.get("/citation-protocol")
async def get_citation_protocol():
    engine = get_rule_engine()
    return {"citation_protocol": engine.get_citation_protocol()}


@router.get("/triggers/{event_type}")
async def get_map_triggers(event_type: str):
    engine = get_rule_engine()
    return {"event_type": event_type, "triggers": engine.get_triggers_for_event(event_type)}


@router.post("/validate")
async def validate_decision(data: dict):
    engine = get_rule_engine()
    return engine.validate(data.get("decision_type", ""), data.get("factors", {}))


@router.post("/cite")
async def generate_citation(data: dict):
    engine = get_rule_engine()
    return {"citation": engine.cite(data.get("rule_id", ""), data.get("explanation", ""))}


# ── Intelligence Panel ──

@router.get("/panel/{node_type}/{node_id}")
async def intelligence_panel(node_type: str, node_id: str, db: AsyncSession = Depends(get_db)):
    """Aggregate 6-layer data for the Intelligence Panel of a given node.

    Returns structured data for the 7-tab panel:
    status / assessment / direction / learning / resources / data / business
    """
    try:
        uid = uuid.UUID(node_id)
    except ValueError:
        raise HTTPException(400, "Invalid node ID")

    engine = get_rule_engine()
    panel = {"node_id": str(uid), "node_type": node_type, "data": {}, "rules_cited": []}

    # Validate node_type against Universe Registry
    node_meta = get_registry().get_node_type(node_type)
    if not node_meta:
        raise HTTPException(400, f"Unknown node type: {node_type}")

    if node_type == "company":
        company = await db.get(Company, uid)
        if not company:
            raise HTTPException(404, "Company not found")

        # Layer 1: Node
        panel["data"]["node"] = {
            "name": company.name, "entity_type": company.entity_type,
            "geo_score": company.geo_score or 0, "industry_id": company.industry_id,
        }

        # Layer 2: Graph — relationships + competitors
        rel_count = (await db.execute(
            select(func.count(Relationship.id)).where(Relationship.source_id == uid)
        )).scalar() or 0
        competitors = (await db.execute(
            select(Competitor).where(Competitor.company_id == str(uid)).limit(5)
        )).scalars().all()
        panel["data"]["graph"] = {
            "relationship_count": rel_count,
            "competitors": [{"id": str(c.id), "name": getattr(c, "competitor_name", "Unknown")} for c in competitors],
        }

        # Layer 3: Dynamic — recent geo_events
        geo_events = (await db.execute(
            select(GeoEvent).order_by(GeoEvent.created_at.desc()).limit(5)
        )).scalars().all()
        panel["data"]["dynamic"] = {
            "recent_events": [{"id": str(ge.id), "type": getattr(ge, "event_type", ""),
                               "desc": getattr(ge, "description", ""), "impact": getattr(ge, "impact_score", 0)}
                              for ge in geo_events],
        }

        # Layer 4: Evolution — growth stage
        gs = (await db.execute(
            select(GrowthStage).where(and_(GrowthStage.node_id == uid, GrowthStage.node_type == "company"))
        )).scalar_one_or_none()
        panel["data"]["evolution"] = {
            "growth_stage": {
                "stage": getattr(gs, "current_stage", "unknown") if gs else "unknown",
                "level": getattr(gs, "stage_level", 1) if gs else 1,
                "progress": getattr(gs, "stage_progress", 0) if gs else 0,
            } if gs else None,
        }

        # Layer 5: Intelligence — evidence + capabilities + reputation
        ev_count = (await db.execute(
            select(func.count(Evidence.id)).where(Evidence.entity_id == uid)
        )).scalar() or 0
        cap_count = (await db.execute(
            select(func.count(Capability.id)).where(Capability.company_id == uid)
        )).scalar() or 0
        rep = (await db.execute(
            select(Reputation).where(and_(Reputation.node_id == uid, Reputation.node_type == "company"))
        )).scalar_one_or_none()
        panel["data"]["intelligence"] = {
            "evidence_count": ev_count,
            "capability_count": cap_count,
            "reputation": {
                "total_score": rep.total_score if rep else 0,
                "level": getattr(rep, "reputation_level", "N/A") if rep else "N/A",
                "rank": getattr(rep, "industry_rank", 0) if rep else 0,
            } if rep else None,
        }

        # Layer 0: Applicable Rules
        panel["rules_cited"] = [
            engine.cite("R01", "Capability-evidence flywheel drives enterprise growth"),
            engine.cite("R04", f"Growth path for {company.name}: Entry -> Active -> Established -> Influencer -> Ecosystem Node"),
            engine.cite("R09", "Reputation is data-driven, cannot be manually altered"),
        ]

    if node_type == "provider":
        provider = await db.get(Provider, uid)
        if not provider:
            raise HTTPException(404, "Provider not found")

        caps = (await db.execute(
            select(ProviderCapability).where(ProviderCapability.provider_id == uid)
        )).scalars().all()
        ev_count = (await db.execute(
            select(func.count(Evidence.id)).where(Evidence.entity_id == uid)
        )).scalar() or 0
        rep = (await db.execute(
            select(Reputation).where(and_(Reputation.node_id == uid, Reputation.node_type == "provider"))
        )).scalar_one_or_none()

        panel["data"]["node"] = {
            "name": f"Provider {str(uid)[:8]}",
            "is_verified": getattr(provider, "is_verified", False),
            "trust_score": getattr(provider, "trust_score", 0),
            "geo_score": getattr(provider, "geo_score", 0),
        }
        panel["data"]["graph"] = {"capability_count": len(caps)}
        panel["data"]["intelligence"] = {
            "evidence_count": ev_count,
            "reputation": {
                "total_score": rep.total_score if rep else 0,
                "level": getattr(rep, "reputation_level", "N/A") if rep else "N/A",
            } if rep else None,
        }
        panel["rules_cited"] = [
            engine.cite("R02", "AI recommendation: capability + evidence + reputation"),
            engine.cite("R07", "Marketplace is the natural business exit"),
        ]

    if node_type == "industry":
        industry = await db.get(Industry, uid)
        if not industry:
            raise HTTPException(404, "Industry not found")

        cc = (await db.execute(
            select(func.count(Company.id)).where(Company.industry_id == str(uid))
        )).scalar() or 0
        pc = (await db.execute(
            select(func.count(Provider.id))
        )).scalar() or 0

        panel["data"]["node"] = {"name": industry.name, "code": industry.code}
        panel["data"]["graph"] = {"company_count": cc, "provider_count": pc}
        panel["rules_cited"] = [
            engine.cite("R03", f"Industry '{industry.name}' auto-evolves via new capabilities and relationships"),
            engine.cite("R05", "Five views = one Universe, cross-highlight active"),
        ]

    if node_type not in ("company", "provider", "industry"):
        raise HTTPException(400, f"Unsupported node type: {node_type}")

    # Summarize panel structure
    panel["panel_sections"] = {
        "status": {"available": True, "summary": "Node identity and core scores"},
        "assessment": {"available": node_type in ("company",), "summary": "Run GEO detection and view agent reports"},
        "direction": {"available": node_type in ("company", "provider"), "summary": "Growth direction and gap analysis"},
        "learning": {"available": False, "summary": "Courses and certification paths (Sprint 4.2)"},
        "resources": {"available": False, "summary": "Expert and tool connections (Sprint 4.2)"},
        "data": {"available": True, "summary": "Evidence, capabilities, relationships, competitors"},
        "business": {"available": node_type in ("company", "provider"), "summary": "Candidate providers and market demands"},
    }

    return panel


# ---- Future Connection Engine (Phase C4) ----

@router.get("/connections/{node_type}/{node_id}")
async def discover_connections(node_type: str, node_id: str):
    """Discover future-path-based connections for a node.

    Not tag matching. Finds nodes that help reach future states.
    Pipeline: Possibility Graph -> Connection Needs -> Candidate Scoring.
    """
    if node_type not in ("company", "provider"):
        raise HTTPException(400, f"Unsupported node type for connections: {node_type}")
    engine = get_connection_engine()
    try:
        report = engine.discover_connections(node_id, node_type)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(500, f"Connection discovery failed: {str(e)}")


@router.post("/connections/record")
async def record_connection(data: dict):
    """Record a connection made between nodes and its outcome score."""
    engine = get_connection_engine()
    return engine.record_connection(
        node_id=data.get("node_id", ""),
        candidate_id=data.get("candidate_id", ""),
        future_state=data.get("future_state", ""),
        outcome_score=data.get("outcome_score", 0.0),
    )


@router.get("/connections/{node_id}/history")
async def get_connection_history(node_id: str):
    """Get connection history for a node."""
    engine = get_connection_engine()
    return engine.get_connection_history(node_id)


# ---- Reputation Engine (Phase C5.1) ----

@router.post("/reputation/event")
async def record_reputation_event(data: dict, db: AsyncSession = Depends(get_db)):
    """Record a reputation event. ONLY way to change reputation. No set.

    C6.1 Gate 0-2: every event is durably persisted; DB is the source of truth.
    """
    engine = get_reputation_engine()
    event = engine.record_event(
        node_id=data.get("node_id", ""),
        node_type=data.get("node_type", "company"),
        event_type=data.get("event_type", ""),
        description=data.get("description", ""),
        source_type=data.get("source_type", "self_report"),
        source_id=data.get("source_id", ""),
        evidence_refs=data.get("evidence_refs", []),
        timestamp=data.get("timestamp"),
    )
    try:
        await engine.persist_event(db, event)
        await db.commit()
    except Exception:
        await db.rollback()
    return event.to_dict()


@router.get("/reputation/node/{node_id}")
async def get_reputation_profile(node_id: str, db: AsyncSession = Depends(get_db)):
    """Get a node's reputation profile with full explanation.

    C6.2 lazy restore: if memory has no events for this node, load from DB first.
    """
    engine = get_reputation_engine()
    if not engine.event_store.get_events(node_id):
        try:
            await engine.restore_from_db(db, node_id)
        except Exception:
            pass
    exp = engine.get_explanation(node_id)
    return exp.to_dict()


@router.post("/reputation/restore/{node_id}")
async def restore_reputation(node_id: str, data: dict = None, db: AsyncSession = Depends(get_db)):
    """C6.1 Gate 0-2: restore a node's reputation from durable DB events."""
    node_type = (data or {}).get("node_type", "company")
    engine = get_reputation_engine()
    snap = await engine.restore_from_db(db, node_id, node_type)
    return snap.to_dict()


@router.post("/reputation/rebuild/{node_id}")
async def rebuild_reputation(node_id: str, data: dict = None, db: AsyncSession = Depends(get_db)):
    """C6.1 Gate 0-2: rebuild reputation state by replaying durable events."""
    node_type = (data or {}).get("node_type", "company")
    engine = get_reputation_engine()
    snap = await engine.rebuild(db, node_id, node_type)
    return snap.to_dict()


@router.get("/reputation/history/{node_id}")
async def get_reputation_history(node_id: str):
    """Get all reputation events for a node."""
    engine = get_reputation_engine()
    return engine.get_history(node_id)


@router.post("/reputation/recalculate/{node_id}")
async def recalculate_reputation(node_id: str, data: dict = None):
    """Force recalculate reputation snapshot from all stored events."""
    node_type = (data or {}).get("node_type", "company")
    engine = get_reputation_engine()
    snap = engine.recalculate(node_id, node_type)
    return snap.to_dict()


@router.get("/reputation/snapshots/{node_id}")
async def get_reputation_snapshots(node_id: str):
    """Get historical reputation snapshots."""
    engine = get_reputation_engine()
    return engine.get_snapshot_history(node_id)


@router.post("/reputation/seed/{node_id}")
async def seed_reputation_data(node_id: str, data: dict = None):
    """Seed sample reputation events for testing."""
    node_type = (data or {}).get("node_type", "company")
    engine = get_reputation_engine()
    snap = engine.seed_sample_data(node_id, node_type)
    return snap.to_dict()


# ---- Relationship Lifecycle Engine (Phase C5.2) ----

@router.post("/relationships/create")
async def create_relationship(data: dict):
    engine = get_relationship_engine()
    rel = engine.create_relationship(
        node_a_id=data.get("node_a_id", ""),
        node_b_id=data.get("node_b_id", ""),
        relationship_type=data.get("relationship_type", "partnership"),
        initiated_by=data.get("initiated_by", ""),
    )
    return rel.to_dict()


@router.post("/relationships/{relationship_id}/transition")
async def transition_relationship(relationship_id: str, data: dict):
    engine = get_relationship_engine()
    event = engine.transition(
        relationship_id=relationship_id,
        to_stage=data.get("to_stage", ""),
        event_type=data.get("event_type", ""),
        actor_id=data.get("actor_id", ""),
        outcome_score=data.get("outcome_score", 0.0),
    )
    stage = engine.get_stage_summary(relationship_id)
    return {"event": event.to_dict(), "stage_summary": stage}


@router.post("/relationships/{relationship_id}/event")
async def record_relationship_event(relationship_id: str, data: dict):
    engine = get_relationship_engine()
    event = engine.record_event(
        relationship_id=relationship_id,
        event_type=data.get("event_type", ""),
        actor_id=data.get("actor_id", ""),
        description=data.get("description", ""),
        outcome_score=data.get("outcome_score", 0.0),
    )
    return event.to_dict()


@router.get("/relationships/node/{node_id}")
async def get_node_relationships(node_id: str):
    engine = get_relationship_engine()
    rels = engine.get_node_relationships(node_id)
    return [r.to_dict() for r in rels]


@router.get("/relationships/between/{node_a}/{node_b}")
async def get_relationship_between(node_a: str, node_b: str):
    engine = get_relationship_engine()
    rel = engine.get_relationship(node_a, node_b)
    if not rel:
        return {"status": "not_found"}
    return engine.get_stage_summary(rel.relationship_id)


@router.get("/relationships/{relationship_id}/reputation")
async def get_relationship_reputation(relationship_id: str):
    engine = get_relationship_engine()
    rep = engine.get_reputation(relationship_id)
    if not rep:
        raise HTTPException(404, "Relationship not found")
    return rep.to_dict()


@router.get("/relationships/{relationship_id}/history")
async def get_relationship_history(relationship_id: str):
    engine = get_relationship_engine()
    return engine.get_history(relationship_id)


# ---- Relationship Intelligence Engine (Phase C5.3) ----

from app.universe.relationship_intelligence import (
    get_relationship_intelligence_engine,
    RelationshipIntelligenceEngine,
    RelationshipOpportunity,
)

@router.post("/intelligence/evaluate")
async def evaluate_relationship_opportunity(data: dict):
    """Evaluate WHY two nodes should connect. Fuses C4+C5.1+C5.2+Possibility+Context."""
    engine = get_relationship_intelligence_engine()
    opp = engine.evaluate_pair(
        node_a_id=data.get("node_a_id", ""),
        node_b_id=data.get("node_b_id", ""),
        node_a_name=data.get("node_a_name", ""),
        node_b_name=data.get("node_b_name", ""),
        node_a_type=data.get("node_a_type", "company"),
        node_b_type=data.get("node_b_type", "company"),
    )
    return opp.to_dict()


@router.get("/intelligence/opportunities/{node_id}")
async def get_relationship_opportunities(node_id: str):
    """Get all stored relationship opportunities for a node."""
    engine = get_relationship_intelligence_engine()
    return engine.get_opportunities(node_id)


@router.get("/intelligence/opportunity/{opportunity_id}")
async def get_opportunity_detail(opportunity_id: str):
    """Get a specific opportunity by ID."""
    engine = get_relationship_intelligence_engine()
    result = engine.get_opportunity(opportunity_id)
    if not result:
        raise HTTPException(404, "Opportunity not found")
    return result


@router.post("/intelligence/from-connection-report")
async def intelligence_from_c4(data: dict):
    """Take C4 Connection Report and upgrade candidates to C5.3 opportunities."""
    engine = get_relationship_intelligence_engine()
    return engine.from_connection_report(
        node_id=data.get("node_id", ""),
        node_name=data.get("node_name", ""),
        node_type=data.get("node_type", "company"),
    )


@router.get("/intelligence/relationship-context/{node_a}/{node_b}")
async def get_full_relationship_context(node_a: str, node_b: str):
    """Get full relationship context (C5.2 history + reputation)."""
    engine = get_relationship_intelligence_engine()
    return engine.get_relationship_context(node_a, node_b)


@router.post("/intelligence/seed")
async def seed_intelligence_data():
    """Seed sample data and evaluate opportunities."""
    engine = get_relationship_intelligence_engine()
    return engine.seed_sample_data()

# ---- Opportunity Memory Engine (Phase C5.4) ----

from app.universe.opportunity_memory import (
    get_opportunity_memory_engine,
    ConnectionValueVector,
)

@router.post("/intelligence/accept/{opportunity_id}")
async def accept_opportunity(opportunity_id: str, data: dict = None):
    """Record that a node accepted a relationship opportunity."""
    engine = get_opportunity_memory_engine()
    event = engine.record_accepted(
        opportunity_id=opportunity_id,
        actor_id=(data or {}).get("actor_id", ""),
        reason=(data or {}).get("reason", ""),
    )
    return event.to_dict()


@router.post("/intelligence/reject/{opportunity_id}")
async def reject_opportunity(opportunity_id: str, data: dict = None):
    """Record that a node rejected a relationship opportunity."""
    engine = get_opportunity_memory_engine()
    event = engine.record_rejected(
        opportunity_id=opportunity_id,
        actor_id=(data or {}).get("actor_id", ""),
        reason=(data or {}).get("reason", ""),
    )
    return event.to_dict()


@router.post("/intelligence/outcome/{opportunity_id}")
async def record_opportunity_outcome(opportunity_id: str, data: dict):
    """Record the business outcome of a relationship opportunity.
    Status: pending | in_progress | successful | failed | stalled | cancelled
    """
    engine = get_opportunity_memory_engine()
    vv_data = data.get('value_realized', {})
    value_vector = ConnectionValueVector(
        revenue=vv_data.get('revenue', 0),
        capability=vv_data.get('capability', 0),
        reputation=vv_data.get('reputation', 0),
        knowledge=vv_data.get('knowledge', 0),
        network=vv_data.get('network', 0),
    )
    outcome = engine.record_outcome(
        opportunity_id=opportunity_id,
        status=data.get('status', 'pending'),
        value_realized=value_vector,
        relationship_growth=data.get('relationship_growth', ''),
        reputation_change_a=data.get('reputation_change_a', 0.0),
        reputation_change_b=data.get('reputation_change_b', 0.0),
        notes=data.get('notes', ''),
    )
    return outcome.to_dict()


@router.get("/intelligence/lifecycle/{opportunity_id}")
async def get_opportunity_lifecycle(opportunity_id: str):
    """Get complete lifecycle timeline for an opportunity."""
    engine = get_opportunity_memory_engine()
    lifecycle = engine.get_lifecycle(opportunity_id)
    outcome = engine.get_outcome(opportunity_id)
    return {
        "opportunity_id": opportunity_id,
        "lifecycle": lifecycle,
        "outcome": outcome,
    }


@router.get("/intelligence/stats/{node_id}")
async def get_learning_stats(node_id: str):
    """Get learning stats for a node (accept rate, success rate, avg confidence)."""
    engine = get_opportunity_memory_engine()
    return engine.get_node_stats(node_id)


@router.post("/intelligence/seed-memory")
async def seed_opportunity_memory():
    """Seed sample opportunity memory with accepted/rejected outcomes."""
    engine = get_opportunity_memory_engine()
    return engine.seed_sample_data()


@router.get("/intelligence/adjusted-confidence/{opportunity_id}")
async def get_adjusted_confidence(opportunity_id: str, base: float = 0.5):
    """Get learning-adjusted confidence for an opportunity."""
    engine = get_opportunity_memory_engine()
    adjusted = engine.get_adjusted_confidence(opportunity_id, base)
    return {
        "opportunity_id": opportunity_id,
        "base_confidence": base,
        "adjusted_confidence": adjusted,
        "delta": round(adjusted - base, 2),
    }

# ---- Universe Home Aggregation (Phase D0.2) ----

@router.get("/home/{node_type}/{node_id}")
async def universe_home(node_type: str, node_id: str, db: AsyncSession = Depends(get_db)):
    """Aggregate a node's complete Universe Home view.

    Combines:
      - Context Engine (identity + position + memory + capability + risk + direction)
      - Possibility Graph (30/90/180 day future states + required connections)
      - Memory velocity (growth trend)

    Output drives the Node Cockpit: who I am / where I am / my past / my future.
    """
    if node_type not in ("company", "provider", "industry", "ai_agent", "government"):
        raise HTTPException(400, f"Unsupported node type: {node_type}")

    # Load base data from DB when possible
    extra = {"name": node_id}
    try:
        uid = uuid.UUID(node_id) if len(node_id) == 36 else node_id
        if node_type == "company":
            company = await db.get(Company, uid) if isinstance(uid, uuid.UUID) else None
            if company:
                extra = {
                    "name": company.name,
                    "description": getattr(company, "description", ""),
                    "industry_id": str(company.industry_id) if company.industry_id else "",
                    "geo_score": company.geo_score or 0,
                    "trust_score": getattr(company, "trust_score", 0) or 0,
                    "evidence_count": (await db.execute(
                        select(func.count(Evidence.id)).where(Evidence.entity_id == uid))).scalar() or 0,
                    "capability_count": (await db.execute(
                        select(func.count(Capability.id)).where(Capability.company_id == uid))).scalar() or 0,
                    "certification_count": 0,
                }
                rel_count = (await db.execute(
                    select(func.count(Relationship.id)).where(Relationship.source_id == uid))).scalar() or 0
                extra["relationship_count"] = rel_count
                extra["relationships_list"] = []
        elif node_type == "provider":
            provider = await db.get(Provider, uid) if isinstance(uid, uuid.UUID) else None
            if provider:
                extra = {
                    "name": f"Provider {str(uid)[:8]}",
                    "trust_score": getattr(provider, "trust_score", 0) or 0,
                    "geo_score": getattr(provider, "geo_score", 0) or 0,
                    "evidence_count": (await db.execute(
                        select(func.count(Evidence.id)).where(Evidence.entity_id == uid))).scalar() or 0,
                    "capability_count": (await db.execute(
                        select(func.count(ProviderCapability.id)).where(ProviderCapability.provider_id == uid))).scalar() or 0,
                }
    except Exception:
        pass  # fall back to engine defaults

    # 1. Context Engine — who / where / past / risks / direction
    ctx = get_context_engine().understand(node_id, node_type, extra)

    # 2. Possibility Graph — future states
    possibility = None
    try:
        graph = get_possibility_engine().project(ctx)
        possibility = graph.to_dict()
    except Exception as e:
        possibility = {"error": str(e), "states": {}, "transitions": []}

    # 3. Memory velocity
    velocity = None
    try:
        velocity = get_memory_engine().get_growth_velocity(node_id)
    except Exception:
        velocity = {"trend": "unknown"}

    # 4. Reputation snapshot (compact) — lazy restore from DB (C6.2)
    rep_snap = None
    try:
        re = get_reputation_engine()
        if not re.event_store.get_events(node_id):
            try:
                await re.restore_from_db(db, node_id)
            except Exception:
                pass
        rep = re.get_profile(node_id)
        rep_snap = rep.to_dict() if rep else None
    except Exception:
        rep_snap = None

    return {
        "node_id": node_id,
        "node_type": node_type,
        "identity": ctx.identity,
        "position": ctx.current_position,
        "memory": {
            "timeline": ctx.historical_memory,
            "velocity": velocity,
        },
        "capability": ctx.capability_state,
        "relationship": ctx.relationship_context,
        "industry": ctx.industry_context,
        "future_signals": ctx.future_signals,
        "risk": ctx.risk_assessment,
        "direction": ctx.recommended_direction,
        "reputation": rep_snap,
        "possibility": possibility,
        "computed_at": ctx.computed_at,
    }


# ---- Transaction Engine (Phase C6) — C6-T1 hardened ----

from app.universe.transaction_engine import (
    get_transaction_engine,
    TransactionEngine,
    TransactionScope,
    UniverseTransaction,
)
from app.models.transaction_record import (
    UniverseTransactionRecord,
    TransactionEventRecord,
)
from datetime import datetime as _dt
from sqlalchemy import select as _txselect


async def _tx_record_to_dict(rec: UniverseTransactionRecord) -> dict:
    """Reconstruct a transaction dict from a persisted DB record."""
    scope = rec.scope_json or {}
    return {
        "transaction_id": rec.transaction_id,
        "node_a_id": rec.node_a_id,
        "node_b_id": rec.node_b_id,
        "node_a_name": rec.node_a_name or rec.node_a_id,
        "node_b_name": rec.node_b_name or rec.node_b_id,
        "scope": scope,
        "linked_opportunity_id": rec.linked_opportunity_id or "",
        "relationship_id": rec.relationship_id or "",
        "stage": rec.stage,
        "previous_stage": rec.previous_stage or "",
        "expected_value": rec.expected_value_json or {},
        "milestone_count": rec.milestone_count or 0,
        "milestones_completed": rec.milestones_completed or 0,
        "created_at": rec.created_at.isoformat() if rec.created_at else "",
        "updated_at": rec.updated_at.isoformat() if rec.updated_at else "",
        "outcome": rec.outcome_json,
    }


async def _persist_transaction(db, tx: UniverseTransaction, outcome: dict = None):
    """Upsert transaction state into durable storage."""
    rec = await db.get(UniverseTransactionRecord, tx.transaction_id)
    if not rec:
        rec = UniverseTransactionRecord(transaction_id=tx.transaction_id)
    rec.node_a_id = tx.node_a_id
    rec.node_b_id = tx.node_b_id
    rec.node_a_name = tx.node_a_name
    rec.node_b_name = tx.node_b_name
    rec.stage = tx.stage
    rec.previous_stage = tx.previous_stage
    rec.scope_json = tx.scope.to_dict()
    rec.linked_opportunity_id = tx.linked_opportunity_id or None
    rec.relationship_id = tx.relationship_id or None
    rec.expected_value_json = tx.expected_value.to_dict()
    rec.milestone_count = tx.milestone_count
    rec.milestones_completed = tx.milestones_completed
    if outcome is not None:
        rec.outcome_json = outcome
    db.add(rec)
    await db.commit()


async def _persist_event(db, event) -> None:
    """Persist one transaction event (idempotent by event_id)."""
    exists = await db.get(TransactionEventRecord, event.event_id)
    if exists:
        return
    rec = TransactionEventRecord(
        event_id=event.event_id,
        transaction_id=event.transaction_id,
        event_type=event.event_type,
        actor_id=event.actor_id or None,
        description=event.description or None,
        milestone_index=event.milestone_index,
        details_json=event.details or {},
        timestamp=_dt.fromisoformat(event.timestamp.replace("Z", "+00:00")) if event.timestamp else _dt.utcnow(),
    )
    db.add(rec)
    await db.commit()


def _require_actor(data: dict, tx: UniverseTransaction) -> str:
    """C6-T1 authorization: actor must be one of the transaction parties."""
    actor = (data.get("actor_id") or "").strip()
    if not actor:
        raise HTTPException(400, "actor_id is required")
    if actor not in (tx.node_a_id, tx.node_b_id):
        raise HTTPException(403, "actor_id is not a party of this transaction")
    return actor


@router.post("/transactions/propose")
async def propose_transaction(data: dict, db: AsyncSession = Depends(get_db)):
    """Propose a transaction from a relationship opportunity or node pair.

    Input: {node_a_id, node_b_id, scope:{...}, node_a_name?, node_b_name?, linked_opportunity_id?}
    C6-T1: node_a_id/node_b_id are required; state is persisted.
    """
    node_a = (data.get("node_a_id") or "").strip()
    node_b = (data.get("node_b_id") or "").strip()
    if not node_a or not node_b:
        raise HTTPException(400, "node_a_id and node_b_id are required")
    if node_a == node_b:
        raise HTTPException(400, "node_a_id and node_b_id must differ")

    engine = get_transaction_engine()
    tx = engine.propose(
        node_a_id=node_a,
        node_b_id=node_b,
        scope=data.get("scope", {}),
        node_a_name=data.get("node_a_name", ""),
        node_b_name=data.get("node_b_name", ""),
        linked_opportunity_id=data.get("linked_opportunity_id", ""),
    )
    await _persist_transaction(db, tx)
    # Persist the proposed event
    events = engine.get_transaction_with_history(tx.transaction_id)
    if events and events.get("events"):
        for e in events["events"]:
            from app.universe.transaction_engine import TransactionEvent as _TE
            try:
                await _persist_event(db, _TE(**e))
            except Exception:
                pass
    return engine.get_transaction_with_history(tx.transaction_id)


@router.post("/transactions/{transaction_id}/transition")
async def transition_transaction(transaction_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    """Advance a transaction: agreed | started | milestone_completed | delivered | reviewed.

    C6-T1: actor must be a party; state is persisted.
    """
    engine = get_transaction_engine()
    tx = engine._transactions.get(transaction_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")
    actor = _require_actor(data, tx)
    event = engine.transition(
        transaction_id=transaction_id,
        event_type=data.get("event_type", ""),
        actor_id=actor,
        description=data.get("description", ""),
        milestone_index=data.get("milestone_index", -1),
        details=data.get("details", {}),
    )
    await _persist_event(db, event)
    await _persist_transaction(db, tx)
    return {"event": event.to_dict(), "transaction": engine.get_transaction_with_history(transaction_id)}


@router.post("/transactions/{transaction_id}/complete")
async def complete_transaction(transaction_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    """Complete a transaction: settled | failed | cancelled.

    C6-T1:
      - actor must be a party
      - client reputation_delta values are ignored (server computes)
      - failed/cancelled do not deduct reputation
      - result is persisted
    """
    engine = get_transaction_engine()
    tx = engine._transactions.get(transaction_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")
    actor = _require_actor(data, tx)
    outcome = engine.complete(
        transaction_id=transaction_id,
        status=data.get("status", "settled"),
        value_realized=data.get("value_realized", {}),
        relationship_growth=data.get("relationship_growth", ""),
        notes=data.get("notes", ""),
        actor_id=actor,
    )
    await _persist_transaction(db, tx, outcome.to_dict())
    # Persist any events produced by complete (delivered/reviewed/settled/failed)
    events = engine.get_transaction_with_history(transaction_id)
    if events and events.get("events"):
        from app.universe.transaction_engine import TransactionEvent as _TE
        for e in events["events"]:
            try:
                await _persist_event(db, _TE(**e))
            except Exception:
                pass
    return {"outcome": outcome.to_dict(), "transaction": engine.get_transaction_with_history(transaction_id)}


@router.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    """Get a transaction with full event history (from memory or durable storage)."""
    engine = get_transaction_engine()
    result = engine.get_transaction_with_history(transaction_id)
    if result:
        return result
    rec = await db.get(UniverseTransactionRecord, transaction_id)
    if not rec:
        raise HTTPException(404, "Transaction not found")
    d = await _tx_record_to_dict(rec)
    ev_rows = (await db.execute(
        _txselect(TransactionEventRecord).where(TransactionEventRecord.transaction_id == transaction_id)
        .order_by(TransactionEventRecord.timestamp)
    )).scalars().all()
    d["events"] = [
        {"event_id": e.event_id, "event_type": e.event_type, "actor_id": e.actor_id,
         "description": e.description, "milestone_index": e.milestone_index,
         "details": e.details_json or {}, "timestamp": e.timestamp.isoformat() if e.timestamp else ""}
        for e in ev_rows
    ]
    return d


@router.get("/transactions/node/{node_id}")
async def get_node_transactions(node_id: str, db: AsyncSession = Depends(get_db)):
    """Get all transactions involving a node (memory + durable storage)."""
    engine = get_transaction_engine()
    results = engine.get_node_transactions(node_id)
    recs = (await db.execute(
        _txselect(UniverseTransactionRecord).where(
            (UniverseTransactionRecord.node_a_id == node_id) | (UniverseTransactionRecord.node_b_id == node_id)
        ).order_by(UniverseTransactionRecord.updated_at.desc())
    )).scalars().all()
    seen = {r["transaction_id"] for r in results}
    for rec in recs:
        if rec.transaction_id in seen:
            continue
        d = await _tx_record_to_dict(rec)
        ev_rows = (await db.execute(
            _txselect(TransactionEventRecord).where(TransactionEventRecord.transaction_id == rec.transaction_id)
        )).scalars().all()
        d["events"] = [{"event_id": e.event_id, "event_type": e.event_type,
                        "description": e.description, "timestamp": e.timestamp.isoformat() if e.timestamp else ""}
                       for e in ev_rows]
        results.append(d)
    return results


@router.post("/transactions/seed")
async def seed_transaction():
    """Seed a sample transaction and complete the full loop.

    C6.1 freeze: only allowed in development/test environments.
    """
    import os as _os
    env = (_os.environ.get("APP_ENV") or getattr(settings, "APP_ENV", "development") or "development").lower()
    allowed = ["development", "test"]
    # Read from learning.yaml to keep configuration authoritative
    try:
        import yaml as _yaml
        _p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                           'config', 'universe', 'learning.yaml')
        if _os.path.exists(_p):
            _cfg = _yaml.safe_load(open(_p, encoding='utf-8'))
            allowed = _cfg.get("transactions", {}).get("seed_allowed_environments", allowed)
    except Exception:
        pass
    if env not in allowed:
        raise HTTPException(403, "transaction seed is disabled in this environment (C6.1 freeze)")
    engine = get_transaction_engine()
    return engine.seed_sample_data()
