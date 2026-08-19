"""C7 DemandEvent - why a node is needed.

A DemandEvent records a real need from proposal to outcome:
  actor -> scenario -> objective -> pain -> existing_solution
  -> missing_capability -> matched_nodes -> outcome
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class DemandEvent(Base):
    __tablename__ = "demand_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scenario: Mapped[str] = mapped_column(String(255), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    pain: Mapped[str | None] = mapped_column(Text, nullable=True)
    existing_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_capability: Mapped[str] = mapped_column(String(255), nullable=False)
    decision_stage: Mapped[str] = mapped_column(String(32), default="research")
    involved_nodes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    mentioned_nodes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ai_answer_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    matched_node_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    final_behavior: Mapped[str] = mapped_column(String(32), default="none")
    outcome: Mapped[str] = mapped_column(String(32), default="pending")
    impact_level: Mapped[str] = mapped_column(String(16), default="medium")
    priority: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(32), default="user_report")
    truth_status: Mapped[str] = mapped_column(String(24), default="observed")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    may_affect_real_metrics: Mapped[bool] = mapped_column(Boolean, default=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
