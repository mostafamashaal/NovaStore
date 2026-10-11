from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.conversation import Conversation
    from src.models.customer import Customer
    from src.models.tool_call import ToolCall
    from src.models.approval import Approval

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class AgentRun(Base):
    """ORM model representing a single AI agent execution."""

    __tablename__ = "agent_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'waiting_approval', "
            "'completed', 'failed', 'cancelled')",
            name="agent_runs_status_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    conversation_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("conversations.id"),
        nullable=False,
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

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    input_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    output_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    estimated_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="agent_runs",
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="agent_runs",
    )

    tool_calls: Mapped[list["ToolCall"]] = relationship(
        "ToolCall",
        back_populates="agent_run",
    )

    approvals: Mapped[list["Approval"]] = relationship(
        "Approval",
        back_populates="agent_run",
    )
