import uuid, enum
from datetime import datetime
from sqlalchemy import String,DateTime,Boolean,Integer,Text,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base

class CertLevel(str,enum.Enum):
    L0='L0';L1='L1';L2='L2';L3='L3';L4='L4'
class CertStatus(str,enum.Enum):
    PENDING='pending';AI_REVIEW='ai_review';HUMAN_REVIEW='human_review'
    APPROVED='approved';REJECTED='rejected';EXPIRED='expired';REVOKED='revoked'
class CertEntityType(str,enum.Enum):
    ENTERPRISE='enterprise';INDIVIDUAL='individual';PROVIDER='provider'
    INSTITUTION='institution';OTHER='other'

class Certification(Base):
    __tablename__ = 'certifications'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    entity_type: Mapped[CertEntityType] = mapped_column(SAEnum(CertEntityType),nullable=False)
    level: Mapped[CertLevel] = mapped_column(SAEnum(CertLevel),default=CertLevel.L0)
    cert_type: Mapped[str] = mapped_column(String(32),default='identity')
    status: Mapped[CertStatus] = mapped_column(SAEnum(CertStatus),default=CertStatus.PENDING)
    ai_review_result: Mapped[dict|None] = mapped_column(JSONB,nullable=True)
    reviewer_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True)
    review_comment: Mapped[str|None] = mapped_column(Text,nullable=True)
    evidence_ids: Mapped[list|None] = mapped_column(JSONB,nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    reviewed_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    issued_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    expires_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    revoked_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    extra_data: Mapped[dict|None] = mapped_column("extra_data", JSONB, nullable=True)
    tenant_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)