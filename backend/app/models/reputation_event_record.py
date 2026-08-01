"""Persistent ReputationEvent — the source of truth for reputation (C6.1 Gate 0-2).

The in-memory ReputationEngine remains the runtime calculator, but every
event is durably stored here so reputation can be rebuilt/replayed after
restart. event_id is unique (idempotent append).
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ReputationEventRecord(Base):
    __tablename__ = "reputation_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    node_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(32), default="company")
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    dimension: Mapped[str] = mapped_column(String(32), default="capability")
    impact: Mapped[str] = mapped_column(String(16), default="positive")
    base_weight: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_weight: Mapped[float] = mapped_column(Float, default=1.0)
    source_type: Mapped[str] = mapped_column(String(32), default="self_report")
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_weight: Mapped[float] = mapped_column(Float, default=0.3)
    effective_weight: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_refs: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
