from uuid import UUID

from src.models.ticket import Ticket
from src.repositories.ticket_repository import TicketRepository


class TicketService:
    """Business logic for customer support tickets."""

    def __init__(self, ticket_repository: TicketRepository) -> None:
        self.ticket_repository = ticket_repository

    def list_tickets_for_customer(
        self,
        customer_id: UUID,
    ) -> list[Ticket]:
        """Return all support tickets belonging to a customer."""
        return self.ticket_repository.list_by_customer(customer_id)

    def get_ticket_for_customer(
        self,
        ticket_id: UUID,
        customer_id: UUID,
    ) -> Ticket | None:
        """Return a ticket only if it belongs to the customer."""
        return self.ticket_repository.get_by_id_for_customer(
            ticket_id=ticket_id,
            customer_id=customer_id,
        )
