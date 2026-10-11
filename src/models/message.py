from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.conversation import Conversation
    from src.models.user import User

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Message(Base):
    """ORM model representing a single message in a conversation."""

    __tablename__ = "messages"

    __table_args__ = (
        CheckConstraint(
            "sender_type IN ('customer', 'support_agent', 'ai', 'system', 'tool')",
            name="messages_sender_type_check",
        ),
        CheckConstraint(
            "length(trim(content)) > 0",
            name="messages_content_check",
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

    sender_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    sender_user_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )

    sender_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="sent_messages",
        foreign_keys=[sender_user_id],
    )
