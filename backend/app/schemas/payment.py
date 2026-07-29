from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class PaymentStatusEnum(str, Enum):
    processing = 'processing'
    succeeded = 'succeeded'
    failed = 'failed'
    refunded = 'refunded'

class PaymentTransactionResponse(BaseModel):
    id: UUID
    order_id: UUID
    user_id: UUID
    amount: float
    currency: str
    fee_amount: Optional[float] = None
    method: Optional[str] = None
    provider: Optional[str] = None
    provider_tx_id: Optional[str] = None
    status: PaymentStatusEnum
    error_message: Optional[str] = None
    created_at: datetime
    model_config = {'from_attributes': True}

class PaymentCallbackPayload(BaseModel):
    provider: str
    provider_tx_id: str
    status: str
    amount: float
    currency: str = 'CNY'
    extra_data: Optional[dict] = None
