"""Persistent records for C6 Transaction Engine (C6-T1 security hardening).

The in-memory TransactionEngine remains the runtime; these tables provide
durable audit/state persistence and enable safe recovery after restart.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class UniverseTransactionRecord(Base):
    __tablename__ = "universe_transactions"

    transaction_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    node_a_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    node_b_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    node_a_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    node_b_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stage: Mapped[str] = mapped_column(String(32), nullable=False, default="PROPOSED")
    previous_stage: Mapped[str] = mapped_column(String(32), default="")
    scope_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    linked_opportunity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    relationship_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expected_value_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    milestone_count: Mapped[int] = mapped_column(Integer, default=0)
    milestones_completed: Mapped[int] = mapped_column(Integer, default=0)
    outcome_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class TransactionEventRecord(Base):
    __tablename__ = "transaction_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    milestone_index: Mapped[int] = mapped_column(Integer, default=-1)
    details_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
