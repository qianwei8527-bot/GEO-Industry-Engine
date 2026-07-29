from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class ReviewStatusEnum(str, Enum):
    pending = 'pending'
    verified = 'verified'
    disputed = 'disputed'

class TransactionReviewResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating_quality: int
    rating_communication: int
    rating_timeliness: int
    rating_value: int
    review_text: Optional[str] = None
    status: ReviewStatusEnum
    verified_at: Optional[datetime] = None
    created_at: datetime
    model_config = {'from_attributes': True}

class ReviewSummary(BaseModel):
    total_reviews: int
    avg_quality: float
    avg_communication: float
    avg_timeliness: float
    avg_value: float
    overall_rating: float
