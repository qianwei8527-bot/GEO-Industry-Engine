from dataclasses import dataclass, field
from typing import Optional
from app.domain.entities.entity import Entity, EntityType

@dataclass
class Company(Entity):
    entity_type: EntityType = field(default=EntityType.COMPANY)
    website: Optional[str] = None
    company_size: Optional[str] = None
    geo_score: int = 0
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    subscription_tier: str = "free"
    logo_url: Optional[str] = None
    owner_id: Optional[str] = None
