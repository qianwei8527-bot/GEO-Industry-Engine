"""IdentityProfile — the dynamic identity of any entity in the GEO Universe.

Each entity (Company, Provider, etc.) can have one or more IdentityProfiles
defining how it presents itself in different contexts (企业/服务商/人才/投资者/政府).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class IdentityProfile(Base):
    """A node's identity in the GEO Universe.

    Not a login account. Not a user profile. It answers the question:
    "Who am I in this Universe, and what is my current position?"
    """

    __tablename__ = "identity_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Identity Basics ──
    identity_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="企业/服务商/人才/投资者/政府/AI Agent"
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tagline: Mapped[str | None] = mapped_column(String(500), nullable=True,
        comment="一句话描述：我在Universe中的角色")

    # ── Position: 5D宇宙坐标 ──
    industry_context: Mapped[str | None] = mapped_column(String(255), nullable=True,
        comment="所在产业/赛道（空间坐标）")
    capability_profile: Mapped[dict | None] = mapped_column(JSONB, nullable=True,
        comment="能力画像（能力坐标）")
    competition_position: Mapped[str | None] = mapped_column(String(64), nullable=True,
        comment="竞争位置 e.g. Top 20%（竞争坐标）")
    growth_stage: Mapped[str | None] = mapped_column(String(32), nullable=True,
        comment="成长阶段 Entry/Active/Established/Influencer/Ecosystem Node（时间坐标）")
    reputation_level: Mapped[str | None] = mapped_column(String(16), nullable=True,
        comment="信誉等级 A/AA/AAA（信誉坐标）")

    # ── Scores ──
    geo_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    visibility_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trust_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capability_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Counts (for fast filtering) ──
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    certification_count: Mapped[int] = mapped_column(Integer, default=0)
    relationship_count: Mapped[int] = mapped_column(Integer, default=0)

    # ── Metadata ──
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True,
        comment="是否主身份（一个entity可有多个identity profile）")
    ext_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # ── Relationships ──
    entity = relationship("Entity", lazy="joined")
