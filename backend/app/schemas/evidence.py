from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class EvidenceCreate(BaseModel):
    target_id: uuid.UUID
    claim: str
    source_url: str
    confidence_level: int = 0
    source_type: Optional[str] = None

class EvidenceResponse(BaseModel):
    id: uuid.UUID
    target_id: uuid.UUID
    claim: str
    source_url: str
    confidence_level: int
    source_type: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}
