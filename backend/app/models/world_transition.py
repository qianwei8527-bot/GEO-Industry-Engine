"""C8.3 World State Transition - deterministic, immutable, general."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class WorldStateTransition(Base):
    __tablename__ = "world_state_transitions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transition_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    from_snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("world_state_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    to_snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("world_state_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    world_code: Mapped[str] = mapped_column(String(64), nullable=False)
    world_version: Mapped[str] = mapped_column(String(32), nullable=False)
    state_scope: Mapped[str] = mapped_column(String(24), nullable=False)
    compatibility_result: Mapped[str] = mapped_column(String(24), nullable=False)
    non_comparable_reason: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    from_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    to_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    transition_rule_version: Mapped[str] = mapped_column(String(32), nullable=False)
    transition_config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    change_manifest: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    gap_lifecycle: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    truth_scope_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    transition_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    historical_source_drift: Mapped[bool] = mapped_column(Boolean, default=False)
    fully_auditable: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("from_snapshot_id", "to_snapshot_id", "transition_rule_version", "transition_config_hash", name="uq_world_transition"),)
