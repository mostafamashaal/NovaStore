from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.message import Message
    from src.models.agent_run import AgentRun
    from src.models.customer import Customer
    from src.models.ticket import Ticket

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Conversation(Base):
    """ORM model representing the existing conversations table."""

    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
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

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="conversations",
    )

    agent_runs: Mapped[list["AgentRun"]] = relationship(
        "AgentRun",
        back_populates="conversation",
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="conversation",
    )
