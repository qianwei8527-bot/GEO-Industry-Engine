import uuid, enum
from datetime import datetime
from sqlalchemy import String,DateTime,Numeric,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base
class CompetitorTier(str,enum.Enum):
    DIRECT='direct';ALTERNATIVE='alternative';POTENTIAL='potential';PARTNER='partner'
class Competitor(Base):
    __tablename__ = 'competitors'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255),nullable=False)
    tier: Mapped[CompetitorTier] = mapped_column(SAEnum(CompetitorTier),nullable=False)
    website: Mapped[str|None] = mapped_column(String(500),nullable=True)
    description: Mapped[str|None] = mapped_column(String(2000),nullable=True)
    scores: Mapped[dict|None] = mapped_column(JSONB,nullable=True)
    strengths: Mapped[list|None] = mapped_column(JSONB,nullable=True)
    weaknesses: Mapped[list|None] = mapped_column(JSONB,nullable=True)
    geo_ie_advantage: Mapped[str|None] = mapped_column(String(2000),nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)