from datetime import datetime
from typing import Any
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.agent_run import AgentRun
    from src.models.approval import Approval

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ToolCall(Base):
    """ORM model representing a single AI agent tool invocation."""

    __tablename__ = "tool_calls"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    agent_run_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("agent_runs.id"),
        nullable=False,
    )

    tool_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    arguments: Mapped[dict[str, Any] | list[Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    result: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    agent_run: Mapped["AgentRun"] = relationship(
        "AgentRun",
        back_populates="tool_calls",
    )

    approvals: Mapped[list["Approval"]] = relationship(
        "Approval",
        back_populates="tool_call",
    )
