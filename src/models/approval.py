
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.agent_run import AgentRun
    from src.models.tool_call import ToolCall
    from src.models.ticket import Ticket
    from src.models.user import User


class Approval(Base):
    """ORM model representing a human approval request."""

    __tablename__ = "approvals"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'expired')",
            name="approvals_status_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    agent_run_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("agent_runs.id"),
        nullable=False,
    )

    tool_call_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tool_calls.id"),
        nullable=True,
    )

    ticket_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tickets.id"),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    decided_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    agent_run: Mapped["AgentRun"] = relationship(
        "AgentRun",
        back_populates="approvals",
    )

    tool_call: Mapped["ToolCall | None"] = relationship(
        "ToolCall",
        back_populates="approvals",
        foreign_keys=[tool_call_id],
    )

    ticket: Mapped["Ticket | None"] = relationship(
        "Ticket",
        back_populates="approvals",
        foreign_keys=[ticket_id],
    )

    decided_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="decided_approvals",
        foreign_keys=[decided_by],
    )
