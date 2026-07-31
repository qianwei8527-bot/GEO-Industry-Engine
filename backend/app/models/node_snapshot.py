"""NodeSnapshot — the time-series memory of every node in the GEO Universe.

This is the foundation for Node Evolution. It captures a node's full state
at a point in time, enabling:
- Historical replay (what was this node like 6 months ago?)
- Growth trajectory (is it rising or declining?)
- AI Observation comparison (what changed since last scan?)
"""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class NodeSnapshot(Base):
    """A frozen moment in a node's life.

    Captured periodically (daily/weekly) or on significant events
    (certification granted, geo_score crossed threshold, etc.)
    """

    __tablename__ = "node_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Temporal ──
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True,
        comment="快照日期")
    snapshot_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="daily",
        comment="daily / weekly / event / manual"
    )
    trigger_event: Mapped[str | None] = mapped_column(String(128), nullable=True,
        comment="触发此快照的事件ID或描述")

    # ── 5D Position Snapshot ──
    growth_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    geo_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    visibility_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trust_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capability_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Structural Snapshot ──
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    certification_count: Mapped[int] = mapped_column(Integer, default=0)
    relationship_count: Mapped[int] = mapped_column(Integer, default=0)
    competitor_count: Mapped[int] = mapped_column(Integer, default=0)

    # ── Extended State ──
    position_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True,
        comment="完整5维位置详情（来自Position Engine）")
    capability_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True,
        comment="能力快照")
    reputation_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True,
        comment="信誉快照")
    relationship_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True,
        comment="关键关系快照")

    # ── Change Detection ──
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True,
        comment="自上次快照的变化摘要（由AI Observation Agent生成）")
    score_delta: Mapped[int | None] = mapped_column(Integer, nullable=True,
        comment="GEO Score相比上次快照的变化")
    is_significant: Mapped[bool] = mapped_column(Boolean, default=False,
        comment="是否显著变化（触发事件/通知）")

    # ── Metadata ──
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # ── Relationships ──
    entity = relationship("Entity", lazy="joined")
