"""V10-P0 GEO Project and execution artifact models.

These are generic project lifecycle records: a GEO Project consumes real
realm goals, calls configurable tools, stores artifacts and records outcomes.
No industry-specific columns are introduced.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Float, DateTime, Text, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class GeoProject(Base):
    __tablename__ = "geo_projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    realm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("realm_registry.id", ondelete="CASCADE"), nullable=False, index=True
    )
    realm_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    project_type: Mapped[str] = mapped_column(String(24), default="geo")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_product: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    scenario: Mapped[str | None] = mapped_column(Text, nullable=True)
    problems: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ai_platforms: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    question_set: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    competitors: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    expected_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_state: Mapped[str] = mapped_column(String(24), default="registered")
    status: Mapped[str] = mapped_column(String(24), default="draft")
    operator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="realm_owner")
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    may_affect_real_metrics: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectWorkItem(Base):
    __tablename__ = "project_work_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="planned")
    phase: Mapped[str | None] = mapped_column(String(64), nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    depends_on: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_materials: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    evidence_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    risks: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    reminder_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completion_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_synced_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    operator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    input_manifest: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_manifest: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_fact_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    may_affect_real_metrics: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectArtifact(Base):
    __tablename__ = "project_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_work_items.id", ondelete="SET NULL"), nullable=True, index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    citations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    published_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    delivery_recipient: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    authorization_scope: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_fact_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    may_affect_real_metrics: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ToolExecutionRecord(Base):
    __tablename__ = "tool_execution_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    realm_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("realm_registry.id", ondelete="CASCADE"), nullable=True, index=True
    )
    realm_entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    authorization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("realm_data_authorizations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    authorization_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    work_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_work_items.id", ondelete="SET NULL"), nullable=True, index=True
    )
    operator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(64), nullable=False)
    capability_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    capability_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    capability_type: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    source_mode: Mapped[str] = mapped_column(String(24), default="platform_standard")
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_manifest: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_manifest: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    input_manifest_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_manifest_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_fact_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    execution_source: Mapped[str] = mapped_column(String(24), default="declared")
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_status: Mapped[str] = mapped_column(String(24), default="running")
    config_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    config_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    citations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectOutcome(Base):
    __tablename__ = "project_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outcome_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    outcome_type: Mapped[str] = mapped_column(String(32), nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    evidence_claim_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evidence_claims.id", ondelete="SET NULL"), nullable=True, index=True
    )
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_result_ref: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    metric_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    validation_rule_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    validation_config_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    validation_config_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    validation_reasons: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    operator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
