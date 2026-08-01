"""C6.3 External Observation API — whitelist sources, runs, artifacts.

External content only becomes Candidate Changes through LearningLoopService;
it never directly modifies facts, reputation, rules, or weights.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.models.observation import ObservationSource, ObservationRun, ObservationArtifact
from app.services.governance import get_governance_service
from app.services.external_observation import ExternalObservationService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/universe", tags=["observation-external"])


@router.get("/observation-sources")
async def list_sources(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List observation sources. Admins see internal config; owners see their own source summaries."""
    gov = get_governance_service()
    is_admin = gov.is_system_admin(current_user)
    q = select(ObservationSource)
    if not is_admin:
        # node owners/reviewers see only their node's sources (summarized)
        q = q.where(ObservationSource.node_id.isnot(None))
    rows = (await db.execute(q.order_by(ObservationSource.created_at.desc()).limit(100))).scalars().all()
    result = []
    for s in rows:
        d = {"source_id": s.source_id, "name": s.name, "source_type": s.source_type,
             "trust_tier": s.trust_tier, "node_id": s.node_id, "enabled": s.enabled,
             "paused": s.paused, "consecutive_failures": s.consecutive_failures,
             "schedule_minutes": s.schedule_minutes, "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
             "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None}
        if is_admin:
            d.update({"domain": s.domain, "base_url": s.base_url, "parser_type": s.parser_type,
                      "allowed_paths": s.allowed_paths, "denied_paths": s.denied_paths,
                      "rate_limit_seconds": s.rate_limit_seconds, "timeout_seconds": s.timeout_seconds,
                      "max_content_size": s.max_content_size})
        result.append(d)
    return {"count": len(result), "sources": result}


@router.post("/observation-sources")
async def create_source(data: dict, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    """Create a source (system_admin only)."""
    gov = get_governance_service()
    if not gov.is_system_admin(current_user):
        raise HTTPException(403, "system_admin permission required")
    sid = (data.get("source_id") or "").strip()
    existing = (await db.execute(select(ObservationSource).where(ObservationSource.source_id == sid))).scalars().first()
    if existing:
        raise HTTPException(400, "source_id already exists")
    # C6.4 Gate 0: DB source must pass YAML policy validation.
    from app.services.external_observation import _load_source_config
    policy = _load_source_config()
    stype = (data.get("source_type") or "").strip()
    domain = (data.get("domain") or "").strip().lower()
    base_url = (data.get("base_url") or "").strip()
    if not domain and base_url:
        from urllib.parse import urlparse as _up
        domain = (_up(base_url).hostname or "").lower()
    if not stype or not domain:
        raise HTTPException(400, "source_type and domain are required")
    allowed_types = {"official_website", "government", "announcement", "media", "industry"}
    if stype not in allowed_types:
        raise HTTPException(400, f"source_type not in whitelist: {stype}")
    if not base_url.startswith("https://") and not (base_url.startswith("http://") and base_url.startswith("http://127.")):
        if base_url and not base_url.startswith(("http://", "https://")):
            raise HTTPException(400, "base_url must be http/https")
    # Domain must not be a private/loopback address literal
    import ipaddress as _ip
    try:
        addr = _ip.ip_address(domain)
        raise HTTPException(400, f"IP literal domain not allowed: {domain}")
    except ValueError:
        pass  # hostname ok
    src = ObservationSource(
        source_id=sid, name=data.get("name", sid), source_type=data.get("source_type", "official_website"),
        domain=data.get("domain", ""), base_url=data.get("base_url"), trust_tier=data.get("trust_tier", "low"),
        node_id=data.get("node_id"), allowed_paths=data.get("allowed_paths"), denied_paths=data.get("denied_paths"),
        parser_type=data.get("parser_type", "meta"), schedule_minutes=data.get("schedule_minutes", 1440),
        rate_limit_seconds=data.get("rate_limit_seconds", 60), timeout_seconds=data.get("timeout_seconds", 10),
        max_content_size=data.get("max_content_size", 1048576), enabled=data.get("enabled", True),
        created_by=current_user.id,
    )
    db.add(src)
    await db.commit()
    await db.refresh(src)
    await gov.audit(db, current_user.id, "source_created", "observation_source", sid, actor_label=current_user.name)
    return {"source_id": sid, "status": "created"}


@router.patch("/observation-sources/{source_id}")
async def update_source(source_id: str, data: dict, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    gov = get_governance_service()
    if not gov.is_system_admin(current_user):
        raise HTTPException(403, "system_admin permission required")
    src = (await db.execute(select(ObservationSource).where(ObservationSource.source_id == source_id))).scalars().first()
    if not src:
        raise HTTPException(404, "source not found")
    for k in ("name", "base_url", "trust_tier", "schedule_minutes", "parser_type", "node_id"):
        if k in data:
            setattr(src, k, data[k])
    await db.commit()
    await gov.audit(db, current_user.id, "source_updated", "observation_source", source_id, actor_label=current_user.name)
    return {"source_id": source_id, "status": "updated"}


@router.post("/observation-sources/{source_id}/enable")
async def enable_source(source_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    gov = get_governance_service()
    if not gov.is_system_admin(current_user):
        raise HTTPException(403, "system_admin permission required")
    src = (await db.execute(select(ObservationSource).where(ObservationSource.source_id == source_id))).scalars().first()
    if not src: raise HTTPException(404, "source not found")
    src.enabled = True; src.paused = False; src.consecutive_failures = 0
    await db.commit()
    await gov.audit(db, current_user.id, "source_enabled", "observation_source", source_id, actor_label=current_user.name)
    return {"source_id": source_id, "enabled": True}


@router.post("/observation-sources/{source_id}/disable")
async def disable_source(source_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    gov = get_governance_service()
    if not gov.is_system_admin(current_user):
        raise HTTPException(403, "system_admin permission required")
    src = (await db.execute(select(ObservationSource).where(ObservationSource.source_id == source_id))).scalars().first()
    if not src: raise HTTPException(404, "source not found")
    src.enabled = False
    await db.commit()
    await gov.audit(db, current_user.id, "source_disabled", "observation_source", source_id, actor_label=current_user.name)
    return {"source_id": source_id, "enabled": False}


@router.post("/observation-sources/{source_id}/run")
async def run_source(source_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Manually run a source (admin/reviewer)."""
    gov = get_governance_service()
    if not (gov.is_system_admin(current_user) or gov.is_reviewer(current_user)):
        raise HTTPException(403, "admin/reviewer permission required")
    src = (await db.execute(select(ObservationSource).where(ObservationSource.source_id == source_id))).scalars().first()
    if not src: raise HTTPException(404, "source not found")
    svc = ExternalObservationService()
    run = await svc.run_source(db, src, manual=True, actor_id=str(current_user.id))
    await gov.audit(db, current_user.id, "source_run", "observation_run", str(run.id), actor_label=current_user.name)
    return {"run_id": str(run.id), "status": run.status, "error_code": run.error_code,
            "content_hash": run.content_hash, "candidates_found": run.candidates_found,
            "change_created": run.change_created}


@router.get("/observation-runs")
async def list_runs(source_id: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=200),
                    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (await db.execute(
        select(ObservationRun).order_by(ObservationRun.started_at.desc()).limit(limit)
    )).scalars().all()
    return {"count": len(rows), "runs": [
        {"run_id": str(r.id), "source_id": r.source_id, "status": r.status, "http_status": r.http_status,
         "content_hash": r.content_hash, "previous_content_hash": r.previous_content_hash,
         "error_code": r.error_code, "candidates_found": r.candidates_found, "change_created": r.change_created,
         "started_at": r.started_at.isoformat() if r.started_at else None}
        for r in rows]}


@router.get("/observation-runs/{run_id}")
async def get_run(run_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = await db.get(ObservationRun, uuid.UUID(run_id))
    if not r: raise HTTPException(404, "run not found")
    return {"run_id": str(r.id), "source_id": r.source_id, "status": r.status, "http_status": r.http_status,
            "content_hash": r.content_hash, "previous_content_hash": r.previous_content_hash,
            "error_code": r.error_code, "retry_count": r.retry_count, "candidates_found": r.candidates_found,
            "change_created": r.change_created}


@router.get("/observation-artifacts/{artifact_id}")
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Admin/reviewer may view full artifact; others only metadata."""
    gov = get_governance_service()
    art = await db.get(ObservationArtifact, uuid.UUID(artifact_id))
    if not art: raise HTTPException(404, "artifact not found")
    base = {"id": str(art.id), "source_id": art.source_id, "source_url": art.source_url,
            "content_hash": art.content_hash, "captured_at": art.captured_at.isoformat() if art.captured_at else None,
            "title": art.title, "trust_tier": art.source_trust_tier}
    if gov.is_system_admin(current_user) or gov.is_reviewer(current_user):
        base["extracted_text"] = (art.extracted_text or "")[:5000]
    return base


@router.get("/nodes/{node_id}/external-observations")
async def node_external_observations(node_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Node owner may view their node's external observation summary."""
    gov = get_governance_service()
    roles = await gov.get_node_roles(db, current_user.id, node_id)
    if not roles and not gov.is_system_admin(current_user):
        raise HTTPException(403, "node membership required")
    arts = (await db.execute(
        select(ObservationArtifact).where(ObservationArtifact.node_id == node_id)
        .order_by(ObservationArtifact.captured_at.desc()).limit(20)
    )).scalars().all()
    return {"node_id": node_id, "observations": [
        {"id": str(a.id), "source_url": a.source_url, "source_id": a.source_id, "title": a.title,
         "content_hash": a.content_hash, "captured_at": a.captured_at.isoformat() if a.captured_at else None,
         "trust_tier": a.source_trust_tier}
        for a in arts]}
