from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class GeoEventBase(BaseModel):
    event_type: str
    title: str
    description: Optional[str] = None
    source_node_id: Optional[UUID] = None
    source_node_type: Optional[str] = None
    impact_level: str = 'medium'
    impact_score: float = 0.0

class GeoEventCreate(GeoEventBase):
    pass

class GeoEventResponse(GeoEventBase):
    id: UUID
    is_processed: bool
    event_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
