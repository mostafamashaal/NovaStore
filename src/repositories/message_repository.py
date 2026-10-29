from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.conversation import Conversation
from src.models.message import Message
from src.models.ticket import Ticket


class MessageRepository:
    """Database operations for support conversation messages."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_conversation(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        """Return conversation messages in chronological order."""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def create_customer_reply(
        self,
        *,
        ticket_id: UUID,
        customer_id: UUID,
        sender_user_id: UUID,
        content: str,
    ) -> Message | None:
        """Create a customer reply and its conversation if needed.

        Returns None when the ticket does not belong to the customer.
        Commits the conversation, ticket link, and message together.
        """
        try:
            statement = (
                select(Ticket)
                .where(
                    Ticket.id == ticket_id,
                    Ticket.customer_id == customer_id,
                )
                .with_for_update()
            )
            ticket = self.db.scalars(statement).first()

            if ticket is None:
                return None

            if ticket.status in {"resolved", "closed"}:
                raise ValueError(
                    "Customers cannot reply to resolved or closed tickets."
                )

            if ticket.conversation_id is not None:
                conversation = self.db.get(
                    Conversation,
                    ticket.conversation_id,
                )

                if conversation is None:
                    raise RuntimeError(
                        "Ticket references a conversation that does not exist."
                    )

                if conversation.customer_id != customer_id:
                    raise RuntimeError(
                        "Ticket conversation does not belong to this customer."
                    )
            else:
                conversation = Conversation(
                    id=uuid4(),
                    customer_id=customer_id,
                    status="open",
                )
                self.db.add(conversation)
                self.db.flush()

                ticket.conversation_id = conversation.id

            message = Message(
                id=uuid4(),
                conversation_id=conversation.id,
                sender_type="customer",
                sender_user_id=sender_user_id,
                content=content,
            )
            self.db.add(message)

            self.db.flush()
            conversation.updated_at = message.created_at

            self.db.commit()
            self.db.refresh(message)

            return message

        except Exception:
            self.db.rollback()
            raise
