from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.order import Order
    from src.models.user import User

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class OrderStatusHistory(Base):
    """ORM model representing order status change history."""

    __tablename__ = "order_status_history"

    __table_args__ = (
        CheckConstraint(
            "changed_by_type IN "
            "('customer', 'support_agent', 'admin', 'ai', 'system')",
            name="order_status_history_changed_by_type_check",
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

    old_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    changed_by_user_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    changed_by_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="status_history",
    )

    changed_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="order_status_changes",
        foreign_keys=[changed_by_user_id],
    )
