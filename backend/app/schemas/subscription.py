from pydantic import BaseModel,Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class SubscriptionCreate(BaseModel):
    plan_tier: str = Field(default='free')
    auto_renew: bool = True

class SubscriptionUpgrade(BaseModel):
    target_tier: str

class SubscriptionResponse(BaseModel):
    id: UUID;user_id: UUID;plan_tier: str;status: str
    current_period_start: datetime;current_period_end: datetime
    trial_ends_at: Optional[datetime]=None
    quota_usage: Optional[dict]=None
    model_config = {'from_attributes':True}

class PlanInfo(BaseModel):
    tier_id: str;name: str;price_monthly: Optional[int];description: str
    features: list[str];permissions: list[str];limitations: list[str]