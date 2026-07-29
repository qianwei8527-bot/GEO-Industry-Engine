import enum
import uuid
from datetime import datetime
from sqlalchemy import String,DateTime,Integer,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID,JSONB
from app.database import Base
class ReviewStatus(str,enum.Enum):
    PENDING='pending';VERIFIED='verified';DISPUTED='disputed'
class TransactionReview(Base):
    __tablename__ = 'transaction_reviews'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    reviewee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False,index=True)
    rating_quality: Mapped[int] = mapped_column(Integer,default=5)
    rating_communication: Mapped[int] = mapped_column(Integer,default=5)
    rating_timeliness: Mapped[int] = mapped_column(Integer,default=5)
    rating_value: Mapped[int] = mapped_column(Integer,default=5)
    review_text: Mapped[str|None] = mapped_column(String(2000),nullable=True)
    evidence: Mapped[list|None] = mapped_column(JSONB,nullable=True)
    status: Mapped[ReviewStatus] = mapped_column(SAEnum(ReviewStatus),default=ReviewStatus.PENDING)
    verified_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow)