"""C7.4 Demand Driven Connection candidate.

A ConnectionCandidate is a projection from a DemandEvent gap analysis.
It is NOT a recommendation, NOT a marketplace match, and accepting it
does NOT change reputation.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ConnectionCandidate(Base):
    __tablename__ = "connection_candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    demand_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demand_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_node_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_node_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    connection_type: Mapped[str] = mapped_column(String(32), nullable=False)
    matched_capabilities: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    evidence_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    capability_score: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0)
    trust_score: Mapped[float] = mapped_column(Float, default=0.0)
    connection_score: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    status: Mapped[str] = mapped_column(String(24), default="proposed")
    decision_source: Mapped[str] = mapped_column(String(16), default="rule")
    decision_scope: Mapped[str] = mapped_column(String(24), default="production")
    may_affect_real_metrics: Mapped[bool] = mapped_column(Boolean, default=False)
    outcome: Mapped[str] = mapped_column(String(24), default="pending")
    decided_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    observed_evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    synthetic_evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    rule_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    config_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    config_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deduplication_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "demand_event_id", "target_node_id", "connection_type",
            name="uq_connection_candidates_demand_target_type",
        ),
    )
