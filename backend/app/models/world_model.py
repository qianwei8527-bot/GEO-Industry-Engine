"""C6.8.5 persistence records for the Living World Model."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class WorldModelProposalRecord(Base):
    __tablename__ = "world_model_proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_candidates.id", ondelete="CASCADE"), nullable=True
    )
    candidate_key: Mapped[str] = mapped_column(String(255), index=True)
    concept_name: Mapped[str] = mapped_column(String(255))
    concept_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    ontology_suggestion: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    evidence_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    source_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    emergence_score: Mapped[float] = mapped_column(Float, default=0.0)
    proposed_by: Mapped[str] = mapped_column(String(128))
    reviewed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    law_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    law_explanation: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(128), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    adopted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    registry_update_pending: Mapped[bool] = mapped_column(Boolean, default=True)


class IndustryContextRecord(Base):
    __tablename__ = "industry_contexts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    emerging_concepts: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    proposals: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    evidence_links: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
