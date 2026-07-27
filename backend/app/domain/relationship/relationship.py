from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from datetime import datetime

class RelationType(str, Enum):
    SUPPLIER = "supplier"
    PARTNER = "partner"
    COMPETITOR = "competitor"
    INVESTOR = "investor"
    CUSTOMER = "customer"
    COLLABORATOR = "collaborator"
    SUPPLY_CHAIN = "supply_chain"
    ECOSYSTEM = "ecosystem"

@dataclass
class Relationship:
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    description: Optional[str] = None
    evidence_ids: Optional[List[str]] = None
    id: Optional[str] = None
    created_at: Optional[datetime] = None
