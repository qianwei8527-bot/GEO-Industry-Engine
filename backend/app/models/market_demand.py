import uuid, enum
from datetime import datetime
from sqlalchemy import String,DateTime,Numeric,ForeignKey,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base
class DemandStatus(str,enum.Enum):
    OPEN='open';IN_PROGRESS='in_progress';CLOSED='closed';EXPIRED='expired'
class DemandCategory(str,enum.Enum):
    SERVICE='service';TOOL='tool';DATA='data';KNOWLEDGE='knowledge';TALENT='talent'
class MarketDemand(Base):
    __tablename__ = 'market_demands'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    publisher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    demand_type: Mapped[str] = mapped_column(String(32),default='demand')
    title: Mapped[str] = mapped_column(String(255),nullable=False)
    description: Mapped[str|None] = mapped_column(String(5000),nullable=True)
    category: Mapped[DemandCategory] = mapped_column(SAEnum(DemandCategory),nullable=False)
    industry_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),ForeignKey("industries.id"),nullable=True,index=True)
    urgency_level: Mapped[str] = mapped_column(String(16),default="normal")
    budget_min: Mapped[float|None] = mapped_column(Numeric(12,2),nullable=True)
    budget_max: Mapped[float|None] = mapped_column(Numeric(12,2),nullable=True)
    timeline_days: Mapped[int|None] = mapped_column(Numeric,nullable=True)
    requirements: Mapped[dict|None] = mapped_column(JSONB,nullable=True)
    status: Mapped[DemandStatus] = mapped_column(SAEnum(DemandStatus),default=DemandStatus.OPEN)
    matched_providers: Mapped[list|None] = mapped_column(JSONB,nullable=True)
    view_count: Mapped[int] = mapped_column(Numeric,default=0)
    inquiry_count: Mapped[int] = mapped_column(Numeric,default=0)
    tenant_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
    expires_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)