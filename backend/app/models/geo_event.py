import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class GeoEvent(Base):
    __tablename__ = 'geo_events'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_node_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    source_node_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_node_ids = mapped_column(JSONB, nullable=True)
    impact_level: Mapped[str] = mapped_column(String(20), default='medium')
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    affected_dimensions = mapped_column(JSONB, nullable=True)
    event_data = mapped_column(JSONB, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source_agent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_processed: Mapped[bool] = mapped_column(default=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
