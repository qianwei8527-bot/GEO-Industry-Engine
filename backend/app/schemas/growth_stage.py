from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class GrowthStageBase(BaseModel):
    node_id: UUID
    node_type: str
    current_stage: str = 'unknown'
    stage_level: int = 0
    stage_progress: float = 0.0

class GrowthStageCreate(GrowthStageBase):
    pass

class GrowthStageResponse(GrowthStageBase):
    id: UUID
    missing_capabilities: Optional[List[str]] = None
    recommended_actions: Optional[List[str]] = None
    learning_resources: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
