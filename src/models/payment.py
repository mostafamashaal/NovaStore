
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.order import Order


class Payment(Base):
    """ORM model representing the existing payments table."""

    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "amount >= 0",
            name="payments_amount_check",
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

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    transaction_reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
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

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="payments",
    )