from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ReputationBase(BaseModel):
    node_id: UUID
    node_type: str
    total_score: float = 0.0
    reputation_level: str = 'B'

class ReputationCreate(ReputationBase):
    pass

class ReputationResponse(ReputationBase):
    id: UUID
    capability_score: float = 0.0
    case_score: float = 0.0
    feedback_score: float = 0.0
    certification_score: float = 0.0
    contribution_score: float = 0.0
    ai_recommendation_score: float = 0.0
    case_count: int = 0
    evidence_count: int = 0
    certification_count: int = 0
    industry_rank: Optional[int] = None
    industry_percentile: float = 0.0
    last_evaluated_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
