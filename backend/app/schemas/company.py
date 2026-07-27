from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    company_size: Optional[str] = None
    industry_id: Optional[uuid.UUID] = None
    contact_email: Optional[str] = None

class CompanyResponse(BaseModel):
    id: uuid.UUID
    geo_id: str
    name: str
    description: Optional[str] = None
    entity_type: str
    is_verified: bool
    website: Optional[str] = None
    company_size: Optional[str] = None
    industry_id: Optional[uuid.UUID] = None
    geo_score: Optional[int] = 0
    subscription_tier: str
    tenant_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
