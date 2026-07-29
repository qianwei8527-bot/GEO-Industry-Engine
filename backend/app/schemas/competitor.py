from pydantic import BaseModel,Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class CompetitorCreate(BaseModel):
    name: str=Field(...,max_length=255);tier: str
    website: Optional[str]=None;description: Optional[str]=None
    scores: Optional[dict]=None;strengths: Optional[list[str]]=None
    weaknesses: Optional[list[str]]=None;geo_ie_advantage: Optional[str]=None

class CompetitorResponse(BaseModel):
    id: UUID;name: str;tier: str
    scores: Optional[dict]=None;last_updated: datetime
    model_config = {'from_attributes':True}