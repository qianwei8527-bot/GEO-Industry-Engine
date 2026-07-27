from dataclasses import dataclass
from typing import Optional
from enum import Enum
import uuid
from datetime import datetime

class EntityType(str, Enum):
    COMPANY = "company"
    PERSON = "person"
    PRODUCT = "product"
    ORGANIZATION = "organization"
    AGENT = "agent"
    REGION = "region"

def _generate_geo_id(entity_type: EntityType) -> str:
    prefix = entity_type.value.upper()[:4]
    return f"GEO-{prefix}-{uuid.uuid4().hex[:8].upper()}"

@dataclass
class Entity:
    name: str
    entity_type: EntityType
    description: Optional[str] = None
    is_verified: bool = False
    geo_id: Optional[str] = None
    id: Optional[uuid.UUID] = None
    tenant_id: Optional[uuid.UUID] = None
    region: Optional[str] = None
    lang_tag: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid.uuid4()
        if self.geo_id is None:
            self.geo_id = _generate_geo_id(self.entity_type)
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
