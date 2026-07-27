from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

class CapabilityLevel(IntEnum):
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4

@dataclass(frozen=True)
class Capability:
    name: str
    company_id: str
    level: CapabilityLevel = CapabilityLevel.L1
    description: Optional[str] = None
    category: Optional[str] = None
