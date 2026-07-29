import uuid, enum
from datetime import datetime
from sqlalchemy import String,DateTime,Boolean,Numeric,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base
class PlanTier(str,enum.Enum):
    FREE='free';GROWTH='growth';PRO='pro';BUSINESS='business';ENTERPRISE='enterprise'
class SubStatus(str,enum.Enum):
    TRIALING='trialing';ACTIVE='active';PAST_DUE='past_due';CANCELED='canceled';EXPIRED='expired'
class Subscription(Base):
    __tablename__ = 'subscriptions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    plan_tier: Mapped[PlanTier] = mapped_column(SAEnum(PlanTier),default=PlanTier.FREE)
    status: Mapped[SubStatus] = mapped_column(SAEnum(SubStatus),default=SubStatus.TRIALING)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean,default=False)
    auto_renew: Mapped[bool] = mapped_column(Boolean,default=True)
    trial_ends_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    provider: Mapped[str|None] = mapped_column(String(32),nullable=True)
    provider_subscription_id: Mapped[str|None] = mapped_column(String(255),nullable=True)
    quota_usage: Mapped[dict|None] = mapped_column(JSONB,nullable=True)
    extra_data: Mapped[dict|None] = mapped_column("extra_data", JSONB, nullable=True)
    tenant_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)