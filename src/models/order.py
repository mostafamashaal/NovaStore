
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
    from src.models.customer import Customer
    from src.models.order_item import OrderItem
    from src.models.order_status_history import OrderStatusHistory
    from src.models.payment import Payment
    from src.models.shipment import Shipment


class Order(Base):
    """ORM model representing the existing orders table."""

    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint(
            "status IN ('processing', 'shipped', 'in_transit', "
            "'delivered', 'cancelled')",
            name="orders_status_check",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="orders_total_amount_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    order_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
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

    customer: Mapped["Customer"] = relationship("Customer")

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
    )

    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
    "OrderStatusHistory",
    back_populates="order",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="order",
    )

    shipments: Mapped[list["Shipment"]] = relationship(
        "Shipment",
        back_populates="order",
    )