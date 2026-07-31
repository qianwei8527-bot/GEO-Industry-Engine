"""Universe Identity & NodeSnapshot API — the entry point into the GEO Universe.

Provides:
- Identity Profile CRUD (create/read identity for any entity)
- Node Snapshot creation and query (node lifecycle history)
- Identity Center data aggregation (what a user sees on /identity)
"""

import uuid
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.identity_profile import IdentityProfile
from app.models.node_snapshot import NodeSnapshot
from app.models.company import Company
from app.models.provider import Provider
from app.models.entity import Entity
from app.universe.rules import get_rule_engine
from app.universe.registry import get_registry


router = APIRouter(prefix="/api/v1/universe/identity", tags=["identity"])


# ═══════════════════════════════════════════════════════════
# Identity Profile CRUD
# ═══════════════════════════════════════════════════════════

@router.post("/profile")
async def create_identity_profile(data: dict, db: AsyncSession = Depends(get_db)):
    """Create or update an identity profile for an entity."""
    entity_id = data.get("entity_id")
    if not entity_id:
        raise HTTPException(400, "entity_id is required")

    # Check entity exists
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, f"Entity not found: {entity_id}")

    # Check for existing primary profile
    if data.get("is_primary", True):
        existing = (await db.execute(
            select(IdentityProfile).where(
                IdentityProfile.entity_id == entity_id,
                IdentityProfile.is_primary == True,
            )
        )).scalars().first()
        if existing:
            existing.is_primary = False

    profile = IdentityProfile(
        entity_id=uuid.UUID(entity_id),
        identity_type=data.get("identity_type", "企业"),
        display_name=data.get("display_name", entity.name),
        tagline=data.get("tagline"),
        industry_context=data.get("industry_context"),
        capability_profile=data.get("capability_profile"),
        competition_position=data.get("competition_position"),
        growth_stage=data.get("growth_stage"),
        reputation_level=data.get("reputation_level"),
        geo_score=data.get("geo_score"),
        visibility_score=data.get("visibility_score"),
        trust_score=data.get("trust_score"),
        capability_score=data.get("capability_score"),
        evidence_count=data.get("evidence_count", 0),
        certification_count=data.get("certification_count", 0),
        relationship_count=data.get("relationship_count", 0),
        is_primary=data.get("is_primary", True),
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return {"status": "created", "profile": _profile_to_dict(profile)}


@router.get("/profile/{entity_id}")
async def get_identity_profile(
    entity_id: str,
    identity_type: str = Query(None, description="Filter by identity type"),
    db: AsyncSession = Depends(get_db),
):
    """Get the primary identity profile for an entity."""
    stmt = select(IdentityProfile).where(
        IdentityProfile.entity_id == entity_id,
        IdentityProfile.is_primary == True,
    )
    if identity_type:
        stmt = stmt.where(IdentityProfile.identity_type == identity_type)

    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        # Try to auto-create from entity
        entity = await db.get(Entity, entity_id)
        if not entity:
            raise HTTPException(404, f"Entity not found: {entity_id}")
        # Return a minimal inferred profile
        return {
            "status": "inferred",
            "profile": _infer_profile_from_entity(entity),
            "message": "No explicit identity profile found. This is auto-inferred from entity data.",
        }

    return {"status": "found", "profile": _profile_to_dict(profile)}


@router.get("/profiles")
async def list_identity_profiles(
    identity_type: str = Query(None),
    growth_stage: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List identity profiles with optional filtering."""
    stmt = select(IdentityProfile).where(IdentityProfile.is_primary == True)
    if identity_type:
        stmt = stmt.where(IdentityProfile.identity_type == identity_type)
    if growth_stage:
        stmt = stmt.where(IdentityProfile.growth_stage == growth_stage)

    stmt = stmt.order_by(desc(IdentityProfile.geo_score)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    profiles = result.scalars().all()

    engine = get_rule_engine()
    return {
        "status": "ok",
        "count": len(profiles),
        "profiles": [_profile_to_dict(p) for p in profiles],
        "rules_cited": [
            engine.cite("R06", "Every node is a universe center"),
            engine.cite("R02", "Ranking by AI recommendation formula"),
        ],
    }


# ═══════════════════════════════════════════════════════════
# Node Snapshot
# ═══════════════════════════════════════════════════════════

@router.post("/snapshot")
async def create_snapshot(data: dict, db: AsyncSession = Depends(get_db)):
    """Capture a node's state at this moment in time."""
    entity_id = data.get("entity_id")
    if not entity_id:
        raise HTTPException(400, "entity_id is required")

    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, f"Entity not found: {entity_id}")

    # Get previous snapshot for delta calculation
    prev = (await db.execute(
        select(NodeSnapshot).where(
            NodeSnapshot.entity_id == entity_id
        ).order_by(desc(NodeSnapshot.snapshot_date)).limit(1)
    )).scalars().first()

    geo_score = data.get("geo_score", 0)
    score_delta = geo_score - prev.geo_score if prev and prev.geo_score else None

    snapshot = NodeSnapshot(
        entity_id=uuid.UUID(entity_id),
        snapshot_date=data.get("snapshot_date", date.today().isoformat()),
        snapshot_type=data.get("snapshot_type", "manual"),
        trigger_event=data.get("trigger_event"),
        growth_stage=data.get("growth_stage"),
        geo_score=geo_score,
        visibility_score=data.get("visibility_score"),
        trust_score=data.get("trust_score"),
        capability_score=data.get("capability_score"),
        evidence_count=data.get("evidence_count", 0),
        certification_count=data.get("certification_count", 0),
        relationship_count=data.get("relationship_count", 0),
        competitor_count=data.get("competitor_count", 0),
        position_json=data.get("position_json"),
        capability_json=data.get("capability_json"),
        reputation_json=data.get("reputation_json"),
        relationship_json=data.get("relationship_json"),
        change_summary=data.get("change_summary"),
        score_delta=score_delta,
        is_significant=data.get("is_significant", abs(score_delta) >= 5 if score_delta else False),
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return {"status": "captured", "snapshot": _snapshot_to_dict(snapshot)}


@router.get("/snapshots/{entity_id}")
async def get_snapshots(
    entity_id: str,
    days: int = Query(90, ge=1, le=730, description="Days of history to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get the snapshot history for an entity (its evolution timeline)."""
    since = date.today().replace(day=1)  # placeholder
    stmt = (
        select(NodeSnapshot)
        .where(NodeSnapshot.entity_id == entity_id)
        .order_by(desc(NodeSnapshot.snapshot_date))
        .limit(min(days, 365))  # max 365 snapshots
    )
    result = await db.execute(stmt)
    snapshots = result.scalars().all()

    if not snapshots:
        # Try to create one from current entity state
        entity = await db.get(Entity, entity_id)
        if not entity:
            raise HTTPException(404, f"Entity not found: {entity_id}")
        return {
            "status": "no_history",
            "snapshots": [],
            "message": "No snapshots yet. Create one to start tracking evolution.",
        }

    engine = get_rule_engine()
    return {
        "status": "ok",
        "entity_id": entity_id,
        "count": len(snapshots),
        "snapshots": [_snapshot_to_dict(s) for s in snapshots],
        "evolution_summary": _compute_evolution_summary(snapshots),
        "rules_cited": [
            engine.cite("R03", "Industry map auto-evolves via node changes"),
            engine.cite("R01", "Capability-evidence flywheel drives growth"),
        ],
    }


@router.get("/snapshots/{entity_id}/latest")
async def get_latest_snapshot(entity_id: str, db: AsyncSession = Depends(get_db)):
    """Get the most recent snapshot for an entity."""
    result = await db.execute(
        select(NodeSnapshot)
        .where(NodeSnapshot.entity_id == entity_id)
        .order_by(desc(NodeSnapshot.snapshot_date))
        .limit(1)
    )
    snapshot = result.scalars().first()
    if not snapshot:
        raise HTTPException(404, "No snapshots for this entity")
    return {"status": "ok", "snapshot": _snapshot_to_dict(snapshot)}


# ═══════════════════════════════════════════════════════════
# Evolution Engine — the living node loop
# ═══════════════════════════════════════════════════════════

@router.get("/evolution/{entity_id}")
async def get_evolution_story(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return the full evolution story for an entity.

    This is the core of the "Living Node" concept:
    Identity → Snapshots → Evolution → Growth Path → Connections.

    Returns pairwise comparisons between consecutive snapshots,
    plus an overall trajectory and the next recommended actions.
    """
    # Get all snapshots ordered by date
    result = await db.execute(
        select(NodeSnapshot)
        .where(NodeSnapshot.entity_id == entity_id)
        .order_by(NodeSnapshot.snapshot_date)
    )
    snapshots = result.scalars().all()

    if len(snapshots) < 2:
        # Return basic state — the node exists but hasn't evolved yet
        entity = await db.get(Entity, entity_id)
        profile_result = await db.execute(
            select(IdentityProfile).where(
                IdentityProfile.entity_id == entity_id,
                IdentityProfile.is_primary == True,
            )
        )
        profile = profile_result.scalars().first()

        return {
            "status": "newborn",
            "entity_id": entity_id,
            "entity_name": entity.name if entity else "Unknown",
            "message": "这个节点刚刚进入 Universe，还只有出生记录。随着每次认证、评分更新、关系变化，生命轨迹会自然生长。",
            "snapshot_count": len(snapshots),
            "current_stage": profile.growth_stage if profile else None,
            "evolution_events": [],
            "trajectory": {"trend": "newborn", "message": "等待第一次变化"},
        }

    # Build pairwise evolution events
    engine = get_rule_engine()
    evolution_events = []
    for i in range(1, len(snapshots)):
        prev = snapshots[i - 1]
        curr = snapshots[i]

        geo_delta = (curr.geo_score or 0) - (prev.geo_score or 0)
        trust_delta = (curr.trust_score or 0) - (prev.trust_score or 0)
        vis_delta = (curr.visibility_score or 0) - (prev.visibility_score or 0)
        cap_delta = (curr.capability_score or 0) - (prev.capability_score or 0)

        # Determine what changed
        changes = []
        if geo_delta != 0:
            changes.append({"dimension": "geo", "delta": geo_delta, "direction": "up" if geo_delta > 0 else "down"})
        if trust_delta != 0:
            changes.append({"dimension": "trust", "delta": trust_delta, "direction": "up" if trust_delta > 0 else "down"})
        if vis_delta != 0:
            changes.append({"dimension": "visibility", "delta": vis_delta, "direction": "up" if vis_delta > 0 else "down"})
        if cap_delta != 0:
            changes.append({"dimension": "capability", "delta": cap_delta, "direction": "up" if cap_delta > 0 else "down"})
        if prev.growth_stage != curr.growth_stage:
            changes.append({"dimension": "growth_stage", "from": prev.growth_stage, "to": curr.growth_stage})

        # Generate evolution insight
        insight = _generate_evolution_insight(prev, curr, changes)

        event = {
            "sequence": i,
            "from_date": prev.snapshot_date.isoformat() if prev.snapshot_date else None,
            "to_date": curr.snapshot_date.isoformat() if curr.snapshot_date else None,
            "trigger": curr.trigger_event or curr.change_summary or "周期性快照",
            "changes": changes,
            "scores": {
                "geo": {"from": prev.geo_score, "to": curr.geo_score, "delta": geo_delta},
                "trust": {"from": prev.trust_score, "to": curr.trust_score, "delta": trust_delta},
                "visibility": {"from": prev.visibility_score, "to": curr.visibility_score, "delta": vis_delta},
                "capability": {"from": prev.capability_score, "to": curr.capability_score, "delta": cap_delta},
            },
            "insight": insight,
            "is_significant": curr.is_significant or abs(geo_delta) >= 5 or prev.growth_stage != curr.growth_stage,
            "rules_cited": [
                engine.cite("R01", "Capability-evidence flywheel: each change feeds the next"),
                engine.cite("R04", f"Growth stage: {prev.growth_stage} → {curr.growth_stage}" if prev.growth_stage != curr.growth_stage else "Growth stage unchanged"),
            ] if prev.growth_stage != curr.growth_stage else [
                engine.cite("R01", "Capability-evidence flywheel"),
            ],
        }
        evolution_events.append(event)

    # Overall trajectory
    latest = snapshots[-1]
    first = snapshots[0]
    total_geo_delta = (latest.geo_score or 0) - (first.geo_score or 0)
    span = (latest.snapshot_date - first.snapshot_date).days if latest.snapshot_date and first.snapshot_date else 0

    if total_geo_delta > 10:
        trajectory_trend = "strong_rising"
        trajectory_message = "持续上升——能力、证据、信誉的飞轮正在加速"
    elif total_geo_delta > 3:
        trajectory_trend = "rising"
        trajectory_message = "稳步成长——每个关键动作都在积累"
    elif total_geo_delta < -5:
        trajectory_trend = "declining"
        trajectory_message = "需要关注——评分下降提示某些环节需要加强"
    else:
        trajectory_trend = "stable"
        trajectory_message = "保持稳定——下一步需要新的增长动力"

    # Next recommended actions (from the growth path)
    next_actions = _generate_next_actions(latest, first)

    return {
        "status": "living",
        "entity_id": entity_id,
        "snapshot_count": len(snapshots),
        "span_days": span,
        "trajectory": {
            "trend": trajectory_trend,
            "message": trajectory_message,
            "total_geo_delta": total_geo_delta,
            "stage_from": first.growth_stage,
            "stage_to": latest.growth_stage,
        },
        "current_state": {
            "geo_score": latest.geo_score,
            "trust_score": latest.trust_score,
            "visibility_score": latest.visibility_score,
            "capability_score": latest.capability_score,
            "growth_stage": latest.growth_stage,
            "evidence_count": latest.evidence_count,
            "relationship_count": latest.relationship_count,
        },
        "evolution_events": evolution_events,
        "next_actions": next_actions,
        "rules_cited": [
            engine.cite("R03", "Universe auto-evolves via node changes"),
            engine.cite("R01", "Growth = capability → evidence → reputation → opportunity"),
        ],
    }


def _generate_evolution_insight(prev: NodeSnapshot, curr: NodeSnapshot, changes: list) -> str:
    """Generate a human-readable evolution insight in Chinese."""
    if not changes:
        return "本期无明显变化，节点保持稳定状态。"

    parts = []
    for c in changes:
        dim = c["dimension"]
        if dim == "geo":
            direction = "提升" if c["direction"] == "up" else "下降"
            parts.append(f"GEO 综合评分{direction} {abs(c['delta'])} 分")
        elif dim == "trust":
            direction = "提升" if c["direction"] == "up" else "下降"
            parts.append(f"Trust 信任度{direction} {abs(c['delta'])} 分")
        elif dim == "visibility":
            direction = "加强" if c["direction"] == "up" else "减弱"
            parts.append(f"Visibility 可见度{direction} {abs(c['delta'])} 分")
        elif dim == "capability":
            direction = "增强" if c["direction"] == "up" else "减弱"
            parts.append(f"Capability 能力评分{direction} {abs(c['delta'])} 分")
        elif dim == "growth_stage":
            parts.append(f"成长阶段从「{c['from']}」进入「{c['to']}」")

    insight = "；".join(parts) + "。"

    # Add business interpretation
    if curr.trigger_event:
        insight += f" 触发事件：{curr.trigger_event}。"

    return insight


def _generate_next_actions(latest: NodeSnapshot, first: NodeSnapshot) -> list:
    """Generate recommended next actions based on the node's current state and trajectory."""
    actions = []

    if not latest.geo_score or latest.geo_score < 50:
        actions.append({
            "priority": 1,
            "action": "补充企业 Evidence",
            "why": "GEO 评分偏低，需要增加可验证的证据记录来提升评分",
            "target_dimension": "geo",
        })
    if not latest.evidence_count or latest.evidence_count < 5:
        actions.append({
            "priority": 2,
            "action": "积累行业认证和案例",
            "why": "Evidence 数量不足，认证和案例是最有效的信誉注入方式",
            "target_dimension": "trust",
        })
    if not latest.relationship_count or latest.relationship_count < 3:
        actions.append({
            "priority": 3,
            "action": "扩展产业合作关系",
            "why": "关系节点是生态网络的基础，更多合作 = 更多推荐和商业机会",
            "target_dimension": "visibility",
        })
    if latest.growth_stage and latest.growth_stage in ("Entry", "Active"):
        next_stage_map = {"Entry": "Active", "Active": "Established"}
        actions.append({
            "priority": 4,
            "action": f"进入 {next_stage_map.get(latest.growth_stage, '下一')} 成长阶段",
            "why": "持续提升评分和信誉，解锁更多 Universe 能力",
            "target_dimension": "growth",
        })

    if not actions:
        actions.append({
            "priority": 1,
            "action": "保持当前成长轨迹",
            "why": "各项指标健康，继续积累即可进入下一阶段",
            "target_dimension": "all",
        })

    return actions


# ── Helpers (continuation of existing helpers) ──


def _profile_to_dict(p: IdentityProfile) -> dict:
    return {
        "id": str(p.id),
        "entity_id": str(p.entity_id),
        "identity_type": p.identity_type,
        "display_name": p.display_name,
        "tagline": p.tagline,
        "industry_context": p.industry_context,
        "capability_profile": p.capability_profile,
        "competition_position": p.competition_position,
        "growth_stage": p.growth_stage,
        "reputation_level": p.reputation_level,
        "scores": {
            "geo": p.geo_score,
            "visibility": p.visibility_score,
            "trust": p.trust_score,
            "capability": p.capability_score,
        },
        "counts": {
            "evidence": p.evidence_count,
            "certification": p.certification_count,
            "relationship": p.relationship_count,
        },
        "is_primary": p.is_primary,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def _snapshot_to_dict(s: NodeSnapshot) -> dict:
    return {
        "id": str(s.id),
        "entity_id": str(s.entity_id),
        "snapshot_date": s.snapshot_date.isoformat() if s.snapshot_date else None,
        "snapshot_type": s.snapshot_type,
        "trigger_event": s.trigger_event,
        "scores": {
            "geo": s.geo_score,
            "visibility": s.visibility_score,
            "trust": s.trust_score,
            "capability": s.capability_score,
        },
        "growth_stage": s.growth_stage,
        "counts": {
            "evidence": s.evidence_count,
            "certification": s.certification_count,
            "relationship": s.relationship_count,
            "competitor": s.competitor_count,
        },
        "score_delta": s.score_delta,
        "change_summary": s.change_summary,
        "is_significant": s.is_significant,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def _infer_profile_from_entity(entity: Entity) -> dict:
    """Auto-infer an identity profile from an entity's data."""
    etype = entity.entity_type if hasattr(entity, "entity_type") else "entity"
    type_map = {"company": "企业", "provider": "服务商"}
    return {
        "entity_id": str(entity.id),
        "identity_type": type_map.get(etype, etype),
        "display_name": entity.name if hasattr(entity, "name") else str(entity.id),
        "tagline": None,
        "industry_context": None,
        "growth_stage": "Entry",
        "scores": {"geo": None, "visibility": None, "trust": None, "capability": None},
        "is_primary": True,
        "inferred": True,
    }


def _compute_evolution_summary(snapshots: list) -> dict:
    """Compute a simple evolution summary from a list of snapshots."""
    if len(snapshots) < 2:
        return {"trend": "insufficient_data", "message": "Need at least 2 snapshots"}

    latest = snapshots[0]
    oldest = snapshots[-1]

    geo_delta = (latest.geo_score or 0) - (oldest.geo_score or 0)
    if geo_delta > 5:
        trend = "rising"
    elif geo_delta < -5:
        trend = "declining"
    else:
        trend = "stable"

    stage_changed = latest.growth_stage != oldest.growth_stage

    return {
        "trend": trend,
        "span_days": (latest.snapshot_date - oldest.snapshot_date).days if latest.snapshot_date and oldest.snapshot_date else 0,
        "geo_delta": geo_delta,
        "stage_changed": stage_changed,
        "stage_from": oldest.growth_stage,
        "stage_to": latest.growth_stage,
        "significant_events": sum(1 for s in snapshots if s.is_significant),
    }
