import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class GrowthStage(Base):
    __tablename__ = 'growth_stages'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(32), nullable=False)
    current_stage: Mapped[str] = mapped_column(String(50), nullable=False, default='unknown')
    stage_level: Mapped[int] = mapped_column(Integer, default=0)
    previous_stages = mapped_column(JSONB, nullable=True)
    next_stage_target: Mapped[str | None] = mapped_column(String(50), nullable=True)
    missing_capabilities = mapped_column(JSONB, nullable=True)
    recommended_actions = mapped_column(JSONB, nullable=True)
    learning_resources = mapped_column(JSONB, nullable=True)
    certification_targets = mapped_column(JSONB, nullable=True)
    stage_progress: Mapped[float] = mapped_column(Float, default=0.0)
    stage_history = mapped_column(JSONB, nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
