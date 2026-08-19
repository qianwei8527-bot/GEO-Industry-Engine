"""V10.5 lightweight startup: client intake and AI analysis records.

ClientIntake stores the raw upload/paste source; IntakeAnalysis stores the
extractable structured draft with provenance. owner confirmation only means
the profile may be used for operations, never automatic verification.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ClientIntake(Base):
    __tablename__ = "client_intakes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intake_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    realm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("realm_registry.id", ondelete="CASCADE"), nullable=False, index=True
    )
    realm_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), default="uploaded")
    relationship: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pasted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplemental_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_manifest: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    source_truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class IntakeAnalysis(Base):
    __tablename__ = "intake_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intake_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client_intakes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    realm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("realm_registry.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    analysis_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_next_steps: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    analysis_mode: Mapped[str] = mapped_column(String(32), default="local_heuristic")
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
