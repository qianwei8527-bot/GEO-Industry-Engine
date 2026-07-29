from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class EventCreate(BaseModel):
    entity_id: UUID = Field(..., description='关联实体ID')
    event_type: str = Field(..., max_length=50, description='事件类型: company_news/product_launch/funding/certification/partnership')
    title: str = Field(..., max_length=300)
    event_date: datetime = Field(..., description='事件发生时间')
    description: Optional[str] = Field(None, max_length=5000)
    impact: int = Field(1, ge=1, le=10, description='影响等级 1-10')
    source_url: Optional[str] = Field(None, max_length=1000)

class EventResponse(BaseModel):
    id: UUID
    entity_id: UUID
    event_type: str
    title: str
    event_date: datetime
    description: Optional[str] = None
    impact: int
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = {'from_attributes': True}

class EventSummary(BaseModel):
    total_events: int
    by_type: dict[str, int]
    high_impact_count: int
    recent_count: int
