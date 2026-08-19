"""Generic Brand realm compatibility model."""

import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.models.entity import Entity


class Brand(Entity):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "brand",
    }
