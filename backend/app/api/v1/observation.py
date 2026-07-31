"""Observation API - ingestion endpoint for Universe external signals.

Receives observations from any source (crawler, agent, user, system)
and writes them as CandidateChange records into the Evidence layer.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.candidate_change import CandidateChange
from app.models.geo_event import GeoEvent
from app.models.knowledge_candidate import KnowledgeCandidate

from app.api.v1.knowledge import compute_emergence_score

router = APIRouter(prefix="/api/v1/observation", tags=["observation"])


class ObservationSignal(BaseModel):
    """An external signal submitted to Observation layer."""
    change_type: str = Field(..., description="new_node / new_relationship / score_delta / stage_transition / external_event")
    signal_label: str = Field(..., description="Human-readable label, e.g. 'AI Employee'")
    source: str = Field(default="agent", description="agent / user / api / crawler / system")
    source_detail: Optional[str] = None
    certainty_level: str = Field(default="B", description="A / B / C")
    evidence_summary: Optional[str] = None
    evidence_url: Optional[str] = None
    evidence_data: Optional[dict] = None
    suggested_action: Optional[str] = None
    suggested_node_type: Optional[str] = None
    suggested_capabilities: Optional[list] = None


class PromoteRequest(BaseModel):
    """Request to promote a CandidateChange from pending to acknowledged / Level B to Level A."""
    status: str = Field(default="acknowledged")
    acknowledged_by: Optional[str] = "admin"


@router.post("/ingest")
async def ingest_signal(signal: ObservationSignal, db: AsyncSession = Depends(get_db)):
    """Ingest an external observation signal.

    If a similar signal already exists (same signal_label + change_type),
    increments occurrence_count. Otherwise creates a new CandidateChange.
    """
    # Check for existing similar signal
    existing = (await db.execute(
        select(CandidateChange).where(
            CandidateChange.signal_label == signal.signal_label,
            CandidateChange.change_type == signal.change_type,
        )
    )).scalars().first()

    if existing:
        existing.occurrence_count += 1
        existing.signal_strength = min(1.0, existing.occurrence_count / 10.0)
        existing.updated_at = datetime.utcnow()
        await db.commit()
        return {
            "status": "accumulated",
            "id": str(existing.id),
            "signal_label": existing.signal_label,
            "occurrence_count": existing.occurrence_count,
            "signal_strength": existing.signal_strength,
            "certainty_level": existing.certainty_level,
        }

    cc = CandidateChange(
        id=uuid.uuid4(),
        change_type=signal.change_type,
        signal_label=signal.signal_label,
        source=signal.source,
        source_detail=signal.source_detail,
        certainty_level=signal.certainty_level,
        evidence_summary=signal.evidence_summary,
        evidence_url=signal.evidence_url,
        evidence_data=signal.evidence_data,
        suggested_action=signal.suggested_action,
        suggested_node_type=signal.suggested_node_type,
        suggested_capabilities=signal.suggested_capabilities,
        occurrence_count=1,
        signal_strength=0.1,
        status="pending",
    )
    db.add(cc)
    await db.commit()
    return {
        "status": "created",
        "id": str(cc.id),
        "signal_label": cc.signal_label,
        "occurrence_count": cc.occurrence_count,
        "signal_strength": cc.signal_strength,
        "certainty_level": cc.certainty_level,
    }


@router.get("/signals")
async def list_signals(
    status: Optional[str] = None,
    certainty_level: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List all CandidateChanges, optionally filtered."""
    q = select(CandidateChange)
    if status:
        q = q.where(CandidateChange.status == status)
    if certainty_level:
        q = q.where(CandidateChange.certainty_level == certainty_level)
    q = q.order_by(CandidateChange.occurrence_count.desc()).limit(limit)
    rows = (await db.execute(q)).scalars().all()
    return {
        "count": len(rows),
        "signals": [
            {
                "id": str(r.id),
                "change_type": r.change_type,
                "signal_label": r.signal_label,
                "source": r.source,
                "certainty_level": r.certainty_level,
                "occurrence_count": r.occurrence_count,
                "signal_strength": r.signal_strength,
                "status": r.status,
                "suggested_action": r.suggested_action,
                "suggested_node_type": r.suggested_node_type,
            }
            for r in rows
        ],
    }


@router.post("/signals/{signal_id}/promote")
async def promote_signal(signal_id: str, req: PromoteRequest, db: AsyncSession = Depends(get_db)):
    """Promote a CandidateChange - acknowledge it and optionally convert to geo_event."""
    cc = (await db.execute(
        select(CandidateChange).where(CandidateChange.id == signal_id)
    )).scalars().first()

    if not cc:
        raise HTTPException(404, "Signal not found")

    cc.status = req.status
    cc.acknowledged_by = req.acknowledged_by or "admin"
    cc.updated_at = datetime.utcnow()

    # If promoting to acknowledged, also create a GeoEvent to enter the World Engine pipeline
    if req.status == "acknowledged":
        event = GeoEvent(
            id=uuid.uuid4(),
            event_type="candidate_change_promoted",
            title=f"New signal acknowledged: {cc.signal_label}",
            description=f"Observation detected: {cc.evidence_summary or cc.signal_label}. "
                       f"Occurrence count: {cc.occurrence_count}, suggested action: {cc.suggested_action}.",
            source_node_type=cc.suggested_node_type or "unknown",
            impact_level="medium" if cc.occurrence_count >= 3 else "low",
            impact_score=cc.signal_strength,
            affected_dimensions={"signal_label": cc.signal_label, "suggested_node_type": cc.suggested_node_type},
            source_agent="observation_pipeline",
            is_processed=True,
        )
        db.add(event)
        
    # Auto-create or update KnowledgeCandidate when promoting
    if req.status == "acknowledged" and cc.suggested_node_type:
        existing_kc = (await db.execute(
            select(KnowledgeCandidate).where(
                KnowledgeCandidate.concept_name == cc.signal_label
            )
        )).scalars().first()

        if existing_kc:
            existing_kc.occurrence_count = cc.occurrence_count
            existing_kc.signal_strength = cc.signal_strength
            existing_kc.last_observed_at = datetime.utcnow()
            existing_kc.source_diversity = max(existing_kc.source_diversity, 1)
            persistence = (datetime.utcnow().date() - existing_kc.first_observed_at.date()).days if existing_kc.first_observed_at else 0
            existing_kc.persistence_days = persistence
            existing_kc.emergence_score = compute_emergence_score(
                existing_kc.occurrence_count, existing_kc.persistence_days,
                existing_kc.source_diversity, existing_kc.impact_score
            )
            existing_kc.updated_at = datetime.utcnow()
            cc_ids = (existing_kc.candidate_change_ids or []) + [str(cc.id)]
            existing_kc.candidate_change_ids = list(set(cc_ids))
        else:
            kc = KnowledgeCandidate(
                id=uuid.uuid4(),
                concept_name=cc.signal_label,
                concept_type=cc.suggested_node_type or "unknown",
                recognition_state="observed",
                occurrence_count=cc.occurrence_count,
                signal_strength=cc.signal_strength,
                source_diversity=1,
                first_observed_at=datetime.utcnow(),
                last_observed_at=datetime.utcnow(),
                candidate_change_ids=[str(cc.id)],
                source_type="auto",
            )
            kc.emergence_score = compute_emergence_score(
                kc.occurrence_count, 0, kc.source_diversity, kc.impact_score
            )
            db.add(kc)
    cc.updated_at = datetime.utcnow()
    await db.commit()

    return {
        "status": cc.status,
        "id": str(cc.id),
        "signal_label": cc.signal_label,
        "acknowledged_by": cc.acknowledged_by,
    }


@router.get("/stats")
async def observation_stats(db: AsyncSession = Depends(get_db)):
    """Get summary stats for the Observation layer."""
    total = (await db.execute(select(func.count(CandidateChange.id)))).scalar()
    pending = (await db.execute(
        select(func.count(CandidateChange.id)).where(CandidateChange.status == "pending")
    )).scalar()
    acknowledged = (await db.execute(
        select(func.count(CandidateChange.id)).where(CandidateChange.status == "acknowledged")
    )).scalar()
    # Find signals with high occurrence that suggest new node types
    emerging = (await db.execute(
        select(CandidateChange).where(
            CandidateChange.suggested_node_type.isnot(None),
            CandidateChange.occurrence_count >= 3,
        ).order_by(CandidateChange.occurrence_count.desc())
    )).scalars().all()

    return {
        "total_signals": total,
        "pending": pending,
        "acknowledged": acknowledged,
        "emerging_patterns": [
            {
                "signal_label": e.signal_label,
                "suggested_node_type": e.suggested_node_type,
                "occurrence_count": e.occurrence_count,
                "signal_strength": e.signal_strength,
            }
            for e in emerging
        ],
    }
