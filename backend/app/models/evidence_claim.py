"""C8.1-R Structured EvidenceClaim.

Separates Evidence Authenticity from Claim Support:
  Evidence verified != Claim verified != Binding verified
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class EvidenceClaim(Base):
    __tablename__ = "evidence_claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    predicate_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    object_type: Mapped[str] = mapped_column(String(32), nullable=False)
    object_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    object_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_locator: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    extraction_method: Mapped[str] = mapped_column(String(32), default="structured")
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    verification_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    verification_result: Mapped[str | None] = mapped_column(String(32), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    may_affect_real_metrics: Mapped[bool] = mapped_column(Boolean, default=False)
    claim_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
