"""KnowledgeCandidate - what Universe is learning to understand.

A KnowledgeCandidate represents a concept that Observation has detected
but Universe has not yet fully recognized. It moves through states:
  Observed → Emerging → Recognized → Adopted
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class KnowledgeCandidate(Base):
    __tablename__ = "knowledge_candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # What Universe is trying to understand
    concept_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    concept_type: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown",
        comment="role / capability / organization / product / relationship_type")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # State machine
    recognition_state: Mapped[str] = mapped_column(String(32), nullable=False, default="observed", index=True,
        comment="observed / emerging / recognized / adopted / rejected")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Emergence Score components
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    persistence_days: Mapped[int] = mapped_column(Integer, default=0)
    source_diversity: Mapped[int] = mapped_column(Integer, default=0,
        comment="Number of distinct sources reporting this concept")
    impact_score: Mapped[float] = mapped_column(Float, default=0.0,
        comment="Estimated impact on existing nodes (0-1)")
    emergence_score: Mapped[float] = mapped_column(Float, default=0.0,
        comment="Composite score: f(occurrence, persistence, diversity, impact)")

    # Evidence links
    candidate_change_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True,
        comment="List of CandidateChange IDs that contributed to this concept")
    first_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Recognition metadata
    recognized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recognized_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Suggested Universe integration
    suggested_node_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True,
        comment="If adopted, what fields should the new node type have")
    suggested_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True,
        comment="If adopted, what Universe Rules should apply")

    source_type: Mapped[str] = mapped_column(String(32), default="production",
        comment="production / seed / experiment")
    experiment_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
