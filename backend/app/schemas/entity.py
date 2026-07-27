from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class EntityBase(BaseModel):
    name: str
    entity_type: str
    description: Optional[str] = None
    region: Optional[str] = None
    lang_tag: Optional[str] = None

class EntityCreate(EntityBase):
    pass

class EntityResponse(EntityBase):
    id: uuid.UUID
    geo_id: str
    is_verified: bool
    tenant_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
