from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.ticket import Ticket


class TicketRepository:
    """Repository for database operations on support tickets."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_customer(self, customer_id: UUID) -> list[Ticket]:
        """Return a customer's tickets, newest first."""
        statement = (
            select(Ticket)
            .where(Ticket.customer_id == customer_id)
            .order_by(Ticket.created_at.desc(), Ticket.id.asc())
        )
        return list(self.session.scalars(statement).all())

    def get_by_id_for_customer(
        self,
        ticket_id: UUID,
        customer_id: UUID,
    ) -> Ticket | None:
        """Find a ticket only if it belongs to the specified customer."""
        statement = select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.customer_id == customer_id,
        )
        return self.session.scalar(statement)
