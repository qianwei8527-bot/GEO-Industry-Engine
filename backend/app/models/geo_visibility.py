"""C6.4 AI Answer Observation models.

AI answers are observations, never facts. They cannot raise Reputation.
Citations become candidates for the C6.3 controlled pipeline.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class QuestionSet(Base):
    __tablename__ = "question_sets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    set_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    industry_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    user_intent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="zh")
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    target_entities: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    competitor_entities: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class AIObservationRun(Base):
    __tablename__ = "ai_observation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    question_set_version: Mapped[int] = mapped_column(Integer, default=1)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_usage: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class AIAnswerArtifact(Base):
    __tablename__ = "ai_answer_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    question_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_answer: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    citations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    entity_mentions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    recommendation_order: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    uncertainty: Mapped[str | None] = mapped_column(String(32), nullable=True)
    parser_version: Mapped[str] = mapped_column(String(16), default="1.0")
    data_origin: Mapped[str] = mapped_column(String(16), default="fake")  # fake | real
    observation_mode: Mapped[str] = mapped_column(String(24), default="unknown")
    baseline_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    provider_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class VisibilityResult(Base):
    __tablename__ = "visibility_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    question_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metric_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, default=0.0)
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    provider_count: Mapped[int] = mapped_column(Integer, default=1)
    question_count: Mapped[int] = mapped_column(Integer, default=1)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    calculation_version: Mapped[str] = mapped_column(String(16), default="1.0")
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
