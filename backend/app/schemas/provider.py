from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ProviderCreate(BaseModel):
    entity_id: UUID
    provider_type: str = Field("company", max_length=32)
    pricing_model: Optional[dict] = None

class ProviderUpdate(BaseModel):
    provider_type: Optional[str] = None
    pricing_model: Optional[dict] = None
    is_active: Optional[bool] = None

class ProviderCapabilityCreate(BaseModel):
    provider_id: UUID
    capability_id: UUID
    level: int = Field(1, ge=1, le=5)
    experience_years: float = Field(0.0, ge=0)

class ProviderResponse(BaseModel):
    id: UUID
    entity_id: UUID
    provider_type: str
    trust_score: float
    geo_score: float
    verification_status: str
    is_verified: bool
    is_active: bool
    completed_orders: int
    avg_rating: float
    pricing_model: Optional[dict] = None
    metadata: Optional[dict] = None
    created_at: datetime
    model_config = {"from_attributes": True}

class ProviderCapabilityResponse(BaseModel):
    id: UUID
    provider_id: UUID
    capability_id: UUID
    level: int
    verified: bool
    experience_years: float
    created_at: datetime
    model_config = {"from_attributes": True}
