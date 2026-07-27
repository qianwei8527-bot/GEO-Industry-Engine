from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Industry:
    name: str
    code: str
    level: int = 1
    parent_id: Optional[str] = None
    description: Optional[str] = None
    id: Optional[str] = None
    sort_order: int = 0
