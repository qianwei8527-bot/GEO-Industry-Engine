from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class RelationshipCreate(BaseModel):
    source_id: uuid.UUID
    target_id: uuid.UUID
    relation_type: str
    weight: float = 1.0
    description: Optional[str] = None

class RelationshipResponse(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    target_id: uuid.UUID
    relation_type: str
    weight: float
    description: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}
