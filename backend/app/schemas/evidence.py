from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class EvidenceCreate(BaseModel):
    entity_id: uuid.UUID
    claim: str
    source_url: str
    confidence_level: float = 0
    source_type: Optional[str] = None

class EvidenceResponse(BaseModel):
    id: uuid.UUID
    entity_id: uuid.UUID
    claim: str
    source_url: str
    confidence_level: float
    source_type: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}

