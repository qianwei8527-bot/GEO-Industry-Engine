"""GEO-Industry-Engine Agent Call Chain Logging model. Sprint A+ Phase 3."""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class AgentCallLog(Base):
    """Records every agent invocation for observability, debugging, and auditing."""
    __tablename__ = "agent_call_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)

    success: Mapped[bool] = mapped_column(Boolean, default=True)
    elapsed_ms: Mapped[int] = mapped_column(Integer, default=0)
    tool_calls: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    citations_count: Mapped[int] = mapped_column(Integer, default=0)
    citations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)