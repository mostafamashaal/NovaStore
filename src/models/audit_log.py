
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class AuditLog(Base):
    """ORM model representing an auditable system event."""

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    actor_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )

    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
