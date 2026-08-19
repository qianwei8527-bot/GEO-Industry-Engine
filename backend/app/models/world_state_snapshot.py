"""C8.2 World State Snapshot - general, versioned, immutable."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class WorldStateSnapshot(Base):
    __tablename__ = "world_state_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vertical_worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    world_code: Mapped[str] = mapped_column(String(64), nullable=False)
    world_version: Mapped[str] = mapped_column(String(32), nullable=False)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    state_scope: Mapped[str] = mapped_column(String(24), nullable=False)
    projection_as_of: Mapped[str] = mapped_column(String(64), nullable=False)
    projection_manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregation_rule_version: Mapped[str] = mapped_column(String(32), nullable=False)
    aggregation_config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    dimensions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    truth_distribution: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    gaps: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    unknown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    excluded: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    snapshot_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
