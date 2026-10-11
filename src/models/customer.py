from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.order import Order
    from src.models.conversation import Conversation
    from src.models.agent_run import AgentRun
    from src.models.ticket import Ticket
    from src.models.refund import Refund

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Customer(Base):
    """ORM model representing the existing customers table."""

    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
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

    user: Mapped["User"] = relationship("User", back_populates="customer")

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="customer",
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="customer",
    )

    agent_runs: Mapped[list["AgentRun"]] = relationship(
        "AgentRun",
        back_populates="customer",
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="customer",
    )

    refunds: Mapped[list["Refund"]] = relationship(
        "Refund",
        back_populates="customer",
    )
