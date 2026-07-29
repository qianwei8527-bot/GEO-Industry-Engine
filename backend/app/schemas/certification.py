from pydantic import BaseModel,Field
from typing import Optional,Any
from uuid import UUID
from datetime import datetime
from enum import Enum

class CertLevelEnum(str,Enum):
    L0='L0';L1='L1';L2='L2';L3='L3';L4='L4'
class CertEntityTypeEnum(str,Enum):
    enterprise='enterprise';individual='individual'
    provider='provider';institution='institution';other='other'

class CertificationApply(BaseModel):
    entity_id: UUID
    entity_type: CertEntityTypeEnum
    target_level: CertLevelEnum
    cert_type: str = Field(default='identity',max_length=32)
    evidence_ids: Optional[list[str]] = None
    metadata: Optional[dict] = None

class CertificationReview(BaseModel):
    action: str = Field(...,pattern='^(approve|reject|request_more)$')
    comment: Optional[str] = None

class CertificationResponse(BaseModel):
    id: UUID
    entity_id: UUID
    entity_type: str
    level: str
    status: str
    applied_at: datetime
    issued_at: Optional[datetime]=None
    expires_at: Optional[datetime]=None
    model_config = {'from_attributes':True}