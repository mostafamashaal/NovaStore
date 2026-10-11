from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.order import Order
    from src.models.customer import Customer
    from src.models.user import User
    from src.models.ticket import Ticket


from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Refund(Base):
    """ORM model representing the existing refunds table."""

    __tablename__ = "refunds"

    __table_args__ = (
        CheckConstraint(
            "amount >= 0",
            name="refunds_amount_check",
        ),
        CheckConstraint(
            "status IN ('requested', 'pending_approval', 'approved', "
            "'rejected', 'processing', 'completed', 'failed')",
            name="refunds_status_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    order_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )

    ticket_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tickets.id"),
        nullable=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    requested_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    approved_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="refunds",
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="refunds",
    )

    ticket: Mapped["Ticket | None"] = relationship(
        "Ticket",
        back_populates="refunds",
    )

    requester: Mapped["User | None"] = relationship(
        "User",
        back_populates="requested_refunds",
        foreign_keys=[requested_by],
    )

    approver: Mapped["User | None"] = relationship(
        "User",
        back_populates="approved_refunds",
        foreign_keys=[approved_by],
    )
