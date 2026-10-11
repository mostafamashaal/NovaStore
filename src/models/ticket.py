
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.customer import Customer
    from src.models.user import User


class Ticket(Base):
    """ORM model representing a customer support ticket."""

    __tablename__ = "tickets"

    __table_args__ = (
        CheckConstraint(
            "category IN ('refund', 'complaint', 'damaged_order', "
            "'technical', 'shipping')",
            name="tickets_category_check",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')",
            name="tickets_priority_check",
        ),
        CheckConstraint(
            "status IN ('open', 'in_progress', 'waiting_customer', "
            "'resolved', 'closed')",
            name="tickets_status_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    ticket_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )

    conversation_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("conversations.id"),
        nullable=True,
    )

    assigned_agent_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    customer: Mapped["Customer"] = relationship("Customer")

    assigned_agent: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assigned_agent_id],
    )