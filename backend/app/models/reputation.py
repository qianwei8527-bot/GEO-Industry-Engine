import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class Reputation(Base):
    __tablename__ = 'reputations'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(32), nullable=False)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    capability_score: Mapped[float] = mapped_column(Float, default=0.0)
    case_score: Mapped[float] = mapped_column(Float, default=0.0)
    feedback_score: Mapped[float] = mapped_column(Float, default=0.0)
    certification_score: Mapped[float] = mapped_column(Float, default=0.0)
    contribution_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_recommendation_score: Mapped[float] = mapped_column(Float, default=0.0)
    reputation_level: Mapped[str] = mapped_column(String(10), default='B')
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    certification_count: Mapped[int] = mapped_column(Integer, default=0)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0)
    industry_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    industry_percentile: Mapped[float] = mapped_column(Float, default=0.0)
    dimension_breakdown = mapped_column(JSONB, nullable=True)
    last_evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
