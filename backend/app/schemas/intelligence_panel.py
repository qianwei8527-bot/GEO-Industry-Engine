"""Intelligence Panel Pydantic schemas."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class PanelSection(BaseModel):
    id: str
    name: str
    name_cn: str
    icon: str
    order: int
    fields: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None

class PanelConfig(BaseModel):
    node_type: str
    label: str
    label_cn: str
    enabled_sections: List[str]
    sections: List[PanelSection]

class IntelligencePanelResponse(BaseModel):
    node_id: str
    node_type: str
    node_name: str
    panel_config: PanelConfig
    data: Dict[str, Any]
    universe_rules: Optional[List[str]] = None
