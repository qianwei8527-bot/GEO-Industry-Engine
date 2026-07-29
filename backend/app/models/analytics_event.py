import uuid
from datetime import datetime
from sqlalchemy import String,DateTime,Index
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base

class AnalyticsEvent(Base):
    __tablename__ = 'analytics_events'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(64),nullable=False,index=True)
    user_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True,index=True)
    session_id: Mapped[str|None] = mapped_column(String(128),nullable=True,index=True)
    entity_type: Mapped[str|None] = mapped_column(String(32),nullable=True)
    entity_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True)
    properties: Mapped[dict|None] = mapped_column(JSONB,nullable=True)
    source: Mapped[str|None] = mapped_column(String(32),nullable=True)
    client_ts: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    server_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    tenant_id: Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)

    __table_args__ = (
        Index('ix_analytics_type_user','event_type','user_id'),
        Index('ix_analytics_entity','entity_type','entity_id'),
        Index('ix_analytics_server_ts','server_ts'),
    )