from uuid import UUID

from src.repositories.message_repository import MessageRepository
from src.repositories.ticket_repository import TicketRepository


class TicketReplyNotAllowedError(Exception):
    """Raised when a ticket cannot accept a customer reply."""


class MessageService:
    """Business logic for customer support messages."""

    def __init__(
        self,
        message_repository: MessageRepository,
        ticket_repository: TicketRepository,
    ) -> None:
        self.message_repository = message_repository
        self.ticket_repository = ticket_repository

    def list_messages_for_ticket(
        self,
        *,
        ticket_id: UUID,
        customer_id: UUID,
    ):
        """Return messages only when the ticket belongs to the customer."""
        ticket = self.ticket_repository.get_by_id_for_customer(
            ticket_id=ticket_id,
            customer_id=customer_id,
        )

        if ticket is None:
            return None

        if ticket.conversation_id is None:
            return []

        return self.message_repository.list_by_conversation(
            conversation_id=ticket.conversation_id,
        )

    def create_customer_reply(
        self,
        *,
        ticket_id: UUID,
        customer_id: UUID,
        sender_user_id: UUID,
        content: str,
    ):
        """Create a reply or report why the reply cannot be accepted."""
        try:
            return self.message_repository.create_customer_reply(
                ticket_id=ticket_id,
                customer_id=customer_id,
                sender_user_id=sender_user_id,
                content=content,
            )
        except ValueError as exc:
            raise TicketReplyNotAllowedError(str(exc)) from exc

    def create_support_agent_reply(
        self,
        *,
        ticket_id: UUID,
        sender_user_id: UUID,
        sender_role: str,
        content: str,
    ):
        """Create a reply from an authorized support agent or admin."""
        if sender_role not in {"support_agent", "admin"}:
            raise TicketAgentReplyForbiddenError(
                "Only support agents and admins can reply through this endpoint."
            )

        try:
            return self.message_repository.create_support_agent_reply(
                ticket_id=ticket_id,
                sender_user_id=sender_user_id,
                is_admin=sender_role == "admin",
                content=content,
            )
        except PermissionError as exc:
            raise TicketAgentReplyForbiddenError(str(exc)) from exc
        except ValueError as exc:
            raise TicketReplyNotAllowedError(str(exc)) from exc


class TicketAgentReplyForbiddenError(Exception):
    """Raised when a user is not authorized to reply as a support agent."""
