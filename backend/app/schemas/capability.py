from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CapabilityCreate(BaseModel):
    company_id: uuid.UUID
    name: str
    level: int = 1
    description: Optional[str] = None
    category: Optional[str] = None

class CapabilityResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    level: int
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}
