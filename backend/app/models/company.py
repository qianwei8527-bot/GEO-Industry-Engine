import uuid
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.entity import Entity

class Company(Entity):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), primary_key=True)
    industry_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="SET NULL"), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Sprint 0.5 字段对齐: 以下5个字段来自02_领域模型设计 + 03_数据架构
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    annual_revenue: Mapped[str | None] = mapped_column(String(50), nullable=True)
    business_scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    geo_score: Mapped[int | None] = mapped_column(Integer, default=0)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    subscription_tier: Mapped[str] = mapped_column(String(20), default="free")
    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    capabilities = relationship("Capability", back_populates="company", lazy="selectin", cascade="all, delete-orphan")
    owner = relationship("User", foreign_keys=[owner_id], lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "company",
    }
