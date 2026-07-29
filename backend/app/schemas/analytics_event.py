from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AnalyticsEventCreate(BaseModel):
    event_type: str = Field(..., max_length=64)
    user_id: Optional[UUID] = None
    session_id: Optional[str] = Field(None, max_length=128)
    entity_type: Optional[str] = Field(None, max_length=32)
    entity_id: Optional[UUID] = None
    properties: Optional[dict] = None
    source: Optional[str] = Field(None, max_length=32)
    client_ts: Optional[datetime] = None

class AnalyticsEventBatch(BaseModel):
    events: list[AnalyticsEventCreate] = Field(..., min_length=1, max_length=100)

class AnalyticsEventResponse(BaseModel):
    id: UUID
    event_type: str
    user_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    server_ts: datetime
    created_at: datetime
    model_config = {'from_attributes': True}

class AnalyticsSummary(BaseModel):
    total_events: int
    unique_users: int
    top_event_types: list[dict]
    period_days: int
