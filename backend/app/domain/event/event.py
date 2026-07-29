from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from datetime import datetime

class EventType(str, Enum):
    FUNDING = "funding"
    PRODUCT_LAUNCH = "product_launch"
    PARTNERSHIP = "partnership"
    POLICY = "policy"
    TALENT_MOVE = "talent_move"
    MERGER = "merger"
    REBRAND = "rebrand"

@dataclass
class Event:
    entity_id: str
    event_type: EventType
    title: str
    event_date: Optional[datetime] = None
    description: Optional[str] = None
    impact: int = 1
    source_url: Optional[str] = None
    evidence_ids: Optional[List[str]] = None
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.event_date is None:
            object.__setattr__(self, "event_date", datetime.utcnow())
        if self.created_at is None:
            object.__setattr__(self, "created_at", datetime.utcnow())
