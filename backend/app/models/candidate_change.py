"""CandidateChange model - Observation layer evidence accumulation.

Each CandidateChange represents a signal from an Observation source:
something happened in the world that Universe might need to respond to.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class CandidateChange(Base):
    __tablename__ = "candidate_changes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # What changed
    change_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True,
        comment="new_node / new_relationship / score_delta / stage_transition / external_event")
    signal_label: Mapped[str] = mapped_column(String(255), nullable=False, index=True,
        comment="Human-readable label, e.g. 'AI Employee'")

    # Where it came from
    source: Mapped[str] = mapped_column(String(64), nullable=False,
        comment="agent / user / api / crawler / system")
    source_detail: Mapped[str | None] = mapped_column(String(500), nullable=True,
        comment="Specific agent name, URL, or user ID")

    # How confident we are
    certainty_level: Mapped[str] = mapped_column(String(1), nullable=False, default="B",
        comment="A (deterministic) / B (inferred) / C (governed rule change)")

    # The evidence
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True,
        comment="What was observed, in human-readable form")
    evidence_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    evidence_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Suggested action
    suggested_action: Mapped[str | None] = mapped_column(String(64), nullable=True,
        comment="create / update / relate / notify / propose_node_type")
    suggested_node_type: Mapped[str | None] = mapped_column(String(64), nullable=True,
        comment="If new node type proposed: role / capability / organization / product")
    suggested_capabilities: Mapped[list | None] = mapped_column(JSONB, nullable=True,
        comment="Default capabilities the new node type should have")

    # Accumulation
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1,
        comment="How many times this signal has been observed")
    signal_strength: Mapped[float] = mapped_column(Float, default=0.5)

    # Lifecycle
    status: Mapped[str] = mapped_column(String(32), default="pending",
        comment="pending / acknowledged / promoted / rejected / archived")
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    source_type: Mapped[str] = mapped_column(String(32), default='production', comment='production / seed / experiment')
    experiment_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # ── C6.1 node-level change fields (appended via migration) ──
    node_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_evidence_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    before_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    proposed_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence_level: Mapped[float] = mapped_column(Float, default=0.0)
    impact_level: Mapped[str] = mapped_column(String(16), default="low",
        comment="low / medium / high")
    deduplication_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    affected_engines: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    applicable_rules: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), default="OBSERVED",
        comment="OBSERVED / PENDING_REVIEW / APPROVED / REJECTED / APPLYING / APPLIED / FAILED / SUPERSEDED")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
