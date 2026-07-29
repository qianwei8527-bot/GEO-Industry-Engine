import uuid, enum
from datetime import datetime
from sqlalchemy import String,DateTime,Numeric,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base
class OrderType(str,enum.Enum):
    SUBSCRIPTION_NEW='subscription_new';SUBSCRIPTION_RENEWAL='subscription_renewal'
    SUBSCRIPTION_UPGRADE='subscription_upgrade';ONE_TIME='one_time'
class OrderStatus(str,enum.Enum):
    PENDING='pending';PAID='paid';REFUNDED='refunded';FAILED='failed'
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    order_type: Mapped[OrderType] = mapped_column(SAEnum(OrderType),nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10,2),nullable=False)
    currency: Mapped[str] = mapped_column(String(10),default='CNY')
    tax_amount: Mapped[float|None] = mapped_column(Numeric(10,2),nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus),default=OrderStatus.PENDING)
    items: Mapped[dict|None] = mapped_column(JSONB,nullable=True)
    provider: Mapped[str|None] = mapped_column(String(32),nullable=True)
    provider_order_id: Mapped[str|None] = mapped_column(String(255),nullable=True)
    paid_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    extra_data: Mapped[dict|None] = mapped_column("extra_data", JSONB, nullable=True)
    tenant_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)