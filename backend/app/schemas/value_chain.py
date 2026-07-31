from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ValueChainBase(BaseModel):
    industry_id: UUID
    chain_name: str
    stages: List[Dict[str, Any]] = []
    total_value_estimate: float = 0.0
    growth_rate: float = 0.0

class ValueChainCreate(ValueChainBase):
    pass

class ValueChainResponse(ValueChainBase):
    id: UUID
    participant_count: int = 0
    trend_direction: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
