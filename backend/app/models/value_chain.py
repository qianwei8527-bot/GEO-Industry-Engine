import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class ValueChain(Base):
    __tablename__ = 'value_chains'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    chain_name: Mapped[str] = mapped_column(String(200), nullable=False)
    stages = mapped_column(JSONB, nullable=False, default=list)
    revenue_models = mapped_column(JSONB, nullable=True)
    flow_data = mapped_column(JSONB, nullable=True)
    total_value_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0)
    participant_count: Mapped[int] = mapped_column(Integer, default=0)
    key_players = mapped_column(JSONB, nullable=True)
    trend_direction: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data_source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
