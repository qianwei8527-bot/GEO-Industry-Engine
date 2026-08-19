"""V10.5 issue library: append-only issue records and history events.

IssueRecord stores the immutable original problem plus current operational
state. IssueEvent keeps an append-only trail of AI classification, manual
edits, status changes, evidence links and template decisions.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class IssueRecord(Base):
    __tablename__ = "issue_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    realm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("realm_registry.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    work_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_work_items.id", ondelete="SET NULL"), nullable=True, index=True
    )
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    scenario: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="manual")
    category: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(16), default="normal")
    status: Mapped[str] = mapped_column(String(24), default="new", index=True)
    possible_causes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tried_methods: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    effective_methods: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ineffective_methods: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    final_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), default="owner_manual")
    truth_scope: Mapped[str] = mapped_column(String(24), default="observed")
    version: Mapped[int] = mapped_column(Integer, default=1)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True, index=True)
    classification_status: Mapped[str] = mapped_column(String(24), default="suggested")
    applicability_boundary: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    is_template_candidate: Mapped[bool] = mapped_column(Boolean, default=False)
    template_status: Mapped[str] = mapped_column(String(16), default="none")
    ai_classification: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class IssueEvent(Base):
    __tablename__ = "issue_events"
    __table_args__ = (
        UniqueConstraint("issue_id", "event_version", name="uq_issue_event_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issue_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_version: Mapped[int] = mapped_column(Integer, default=1)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    actor_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
