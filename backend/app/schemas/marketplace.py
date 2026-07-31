from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class DemandStatusEnum(str, Enum):
    open = 'open'
    in_progress = 'in_progress'
    closed = 'closed'
    expired = 'expired'

class DemandCategoryEnum(str, Enum):
    service = 'service'
    tool = 'tool'
    data = 'data'
    knowledge = 'knowledge'
    talent = 'talent'

class MarketDemandCreate(BaseModel):
    demand_type: str = Field('demand', max_length=32)
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category: DemandCategoryEnum
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    timeline_days: Optional[int] = Field(None, ge=1)
    requirements: Optional[dict] = None
    expires_at: Optional[datetime] = None

class MarketDemandResponse(BaseModel):
    id: UUID
    publisher_id: UUID
    demand_type: str
    title: str
    description: Optional[str] = None
    category: DemandCategoryEnum
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    timeline_days: Optional[int] = None
    requirements: Optional[dict] = None
    status: DemandStatusEnum
    view_count: int
    inquiry_count: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    model_config = {'from_attributes': True}

class ReviewCreate(BaseModel):
    transaction_id: UUID
    reviewee_id: UUID
    rating_quality: int = Field(5, ge=1, le=5)
    rating_communication: int = Field(5, ge=1, le=5)
    rating_timeliness: int = Field(5, ge=1, le=5)
    rating_value: int = Field(5, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=2000)
    evidence: Optional[list] = None

class ReviewResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating_quality: int
    rating_communication: int
    rating_timeliness: int
    rating_value: int
    review_text: Optional[str] = None
    status: str
    created_at: datetime
    model_config = {'from_attributes': True}

class MatchResultItem(BaseModel):
    provider_id: str
    score: float
    level: str
    reasons: list[str]
    scores_detail: dict

class MatchResponse(BaseModel):
    demand_id: str
    matches: list[MatchResultItem]
    generated_at: Optional[str] = None

