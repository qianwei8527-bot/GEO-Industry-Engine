from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class IndustryCreate(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    level: int = 1
    description: Optional[str] = None

class IndustryResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    level: int
    description: Optional[str] = None
    sort_order: Optional[int] = 0
    model_config = {"from_attributes": True}

