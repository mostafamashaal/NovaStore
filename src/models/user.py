from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.customer import Customer
    from src.models.document import Document
    from src.models.message import Message
    from src.models.order_status_history import OrderStatusHistory
    from src.models.ticket import Ticket
    from src.models.refund import Refund
    from src.models.approval import Approval
    from src.models.audit_log import AuditLog

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class User(Base):
    """ORM model representing the existing users table."""

    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('customer', 'support_agent', 'admin')",
            name="users_role_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
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

    customer: Mapped["Customer | None"] = relationship(
        "Customer",
        back_populates="user",
        uselist=False,
    )

    sent_messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="sender_user",
        foreign_keys="Message.sender_user_id",
    )

    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="assigned_agent",
        foreign_keys="Ticket.assigned_agent_id",
    )

    uploaded_documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="uploader",
        foreign_keys="Document.uploaded_by",
    )

    order_status_changes: Mapped[list["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory",
        back_populates="changed_by_user",
        foreign_keys="OrderStatusHistory.changed_by_user_id",
    )

    requested_refunds: Mapped[list["Refund"]] = relationship(
        "Refund",
        back_populates="requester",
        foreign_keys="Refund.requested_by",
    )

    approved_refunds: Mapped[list["Refund"]] = relationship(
        "Refund",
        back_populates="approver",
        foreign_keys="Refund.approved_by",
    )

    decided_approvals: Mapped[list["Approval"]] = relationship(
        "Approval",
        back_populates="decided_by_user",
        foreign_keys="Approval.decided_by",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="actor_user",
        foreign_keys="AuditLog.actor_user_id",
    )
