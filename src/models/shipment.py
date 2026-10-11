from datetime import date, datetime
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.order import Order

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Shipment(Base):
    """ORM model representing the existing shipments table."""

    __tablename__ = "shipments"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'shipped', 'in_transit', 'delivered')",
            name="shipments_status_check",
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

    carrier: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    tracking_number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    estimated_delivery: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
        back_populates="shipments",
    )
