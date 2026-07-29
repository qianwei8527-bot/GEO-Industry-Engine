import uuid, enum
from datetime import datetime
from sqlalchemy import String,DateTime,Numeric,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base
class PaymentStatus(str,enum.Enum):
    PROCESSING='processing';SUCCEEDED='succeeded';FAILED='failed';REFUNDED='refunded'
class PaymentTransaction(Base):
    __tablename__ = 'payment_transactions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    amount: Mapped[float] = mapped_column(Numeric(10,2),nullable=False)
    currency: Mapped[str] = mapped_column(String(10),default='CNY')
    fee_amount: Mapped[float|None] = mapped_column(Numeric(10,2),nullable=True)
    method: Mapped[str|None] = mapped_column(String(32),nullable=True)
    provider: Mapped[str|None] = mapped_column(String(32),nullable=True)
    provider_tx_id: Mapped[str|None] = mapped_column(String(255),nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus),default=PaymentStatus.PROCESSING)
    error_message: Mapped[str|None] = mapped_column(String(500),nullable=True)
    extra_data: Mapped[dict|None] = mapped_column("extra_data", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)