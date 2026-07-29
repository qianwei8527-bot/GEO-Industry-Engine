from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class OrderTypeEnum(str, Enum):
    subscription_new = 'subscription_new'
    subscription_renewal = 'subscription_renewal'
    subscription_upgrade = 'subscription_upgrade'
    one_time = 'one_time'

class OrderStatusEnum(str, Enum):
    pending = 'pending'
    paid = 'paid'
    refunded = 'refunded'
    failed = 'failed'

class OrderCreate(BaseModel):
    order_type: OrderTypeEnum
    amount: float = Field(..., gt=0, description='订单金额')
    currency: str = 'CNY'
    tax_amount: Optional[float] = None
    items: Optional[dict] = None

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    order_type: OrderTypeEnum
    amount: float
    currency: str
    tax_amount: Optional[float] = None
    status: OrderStatusEnum
    items: Optional[dict] = None
    provider: Optional[str] = None
    provider_order_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = {'from_attributes': True}
