from dataclasses import dataclass
from typing import Optional
from enum import IntEnum
from datetime import datetime

class ConfidenceLevel(IntEnum):
    L0_SELF_REPORTED = 0
    L1_PLATFORM_VERIFIED = 1
    L2_THIRD_PARTY = 2
    L3_MARKET_VALIDATED = 3
    L4_AI_CROSS_VERIFIED = 4

@dataclass(frozen=True)
class Evidence:
    target_id: str
    claim: str
    source_url: str
    confidence_level: ConfidenceLevel = ConfidenceLevel.L0_SELF_REPORTED
    source_type: Optional[str] = None
    verified_at: Optional[datetime] = None
