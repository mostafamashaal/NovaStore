from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, text
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

    def create(
        self,
        customer_id: UUID,
        category: str,
        priority: str,
        subject: str,
        description: str,
    ) -> Ticket:
        """Create and persist a new support ticket."""
        try:
            sequence_value = self.session.execute(
                text("SELECT nextval('ticket_number_seq')")
            ).scalar_one()

            current_year = datetime.now(timezone.utc).year

            ticket = Ticket(
                id=uuid4(),
                ticket_number=f"TKT-{current_year}-{sequence_value:05d}",
                customer_id=customer_id,
                category=category,
                priority=priority,
                status="open",
                subject=subject,
                description=description,
            )

            self.session.add(ticket)
            self.session.commit()
            self.session.refresh(ticket)

        except Exception:
            self.session.rollback()
            raise

        return ticket

    def update_status(
        self,
        ticket: Ticket,
        status: str,
        resolved_at: datetime | None,
    ) -> Ticket:
        """Update a ticket's status and persist the change."""
        try:
            ticket.status = status
            ticket.updated_at = datetime.now(timezone.utc)
            ticket.resolved_at = resolved_at

            self.session.commit()
            self.session.refresh(ticket)

        except Exception:
            self.session.rollback()
            raise

        return ticket