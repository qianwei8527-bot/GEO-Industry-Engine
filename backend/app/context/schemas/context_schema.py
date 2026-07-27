from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class ScoringSummary(BaseModel):
    relevance_score: float = 0.0
    trust_score: float = 0.0
    geo_score: int = 0
    capability_match: float = 0.0
    overall: float = 0.0


class CompanyProfile(BaseModel):
    id: uuid.UUID
    geo_id: str
    name: str
    entity_type: str
    description: Optional[str] = None
    website: Optional[str] = None
    company_size: Optional[str] = None
    is_verified: bool = False
    subscription_tier: str = "free"
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class IndustryProfile(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    level: int
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


class CapabilityProfile(BaseModel):
    id: uuid.UUID
    name: str
    level: int
    description: Optional[str] = None
    category: Optional[str] = None
    company_id: uuid.UUID

    model_config = {"from_attributes": True}


class CapabilityInfo(BaseModel):
    id: uuid.UUID
    name: str
    level: int
    category: Optional[str] = None


class RelationshipInfo(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    target_id: uuid.UUID
    relation_type: str
    weight: float
    description: Optional[str] = None
    target_name: Optional[str] = None
    target_type: Optional[str] = None


class EventInfo(BaseModel):
    id: uuid.UUID
    event_type: str
    title: str
    occurred_at: datetime
    description: Optional[str] = None
    impact_level: int = 1


class EvidenceInfo(BaseModel):
    id: uuid.UUID
    claim: str
    source_url: str
    confidence_level: int
    source_type: Optional[str] = None
    verified_at: Optional[datetime] = None


class OpportunityInfo(BaseModel):
    title: str
    description: str
    relevance: float
    type: str = "general"


class TrendInfo(BaseModel):
    title: str
    description: str
    direction: str = "stable"
    strength: float = 0.5


class CompanyBrief(BaseModel):
    id: uuid.UUID
    name: str
    geo_score: int = 0
    is_verified: bool = False


class IndustryBrief(BaseModel):
    id: uuid.UUID
    name: str
    code: str


class CompanyContext(BaseModel):
    company: CompanyProfile
    industries: List[IndustryBrief] = []
    capabilities: List[CapabilityInfo] = []
    relationships: List[RelationshipInfo] = []
    events: List[EventInfo] = []
    evidence: List[EvidenceInfo] = []
    scoring: ScoringSummary = ScoringSummary()
    opportunities: List[OpportunityInfo] = []


class IndustryContext(BaseModel):
    industry: IndustryProfile
    companies: List[CompanyBrief] = []
    capabilities: List[CapabilityInfo] = []
    trends: List[TrendInfo] = []
    events: List[EventInfo] = []
    opportunities: List[OpportunityInfo] = []


class CapabilityContext(BaseModel):
    capability: CapabilityProfile
    providers: List[CompanyBrief] = []
    industries: List[IndustryBrief] = []
    relationships: List[RelationshipInfo] = []
    evidence: List[EvidenceInfo] = []


class ContextQueryRequest(BaseModel):
    query: str
    limit: int = 10
    entity_type: Optional[str] = None


class ContextQueryResponse(BaseModel):
    query: str
    results: List[CompanyBrief] = []
    total: int = 0
