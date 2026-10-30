from uuid import UUID

from src.api.schemas.ticket import TicketCreateRequest
from src.models.ticket import Ticket
from src.repositories.ticket_repository import TicketRepository


class TicketStatusTransitionError(Exception):
    """Raised when a requested ticket status transition is not allowed."""


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

    def create_ticket_for_customer(
        self,
        customer_id: UUID,
        ticket_data: TicketCreateRequest,
    ) -> Ticket:
        """Create a ticket for the specified customer."""
        return self.ticket_repository.create(
            customer_id=customer_id,
            category=ticket_data.category,
            priority=ticket_data.priority,
            subject=ticket_data.subject,
            description=ticket_data.description,
        )

    def update_ticket_status_for_customer(
        self,
        ticket_id: UUID,
        customer_id: UUID,
        requested_status: str,
    ) -> Ticket | None:
        """Update a customer's ticket when the transition is permitted."""
        ticket = self.ticket_repository.get_by_id_for_customer(
            ticket_id=ticket_id,
            customer_id=customer_id,
        )

        if ticket is None:
            return None

        allowed_transitions = {
            "open": {"closed"},
            "in_progress": {"closed"},
            "waiting_customer": {"closed"},
            "resolved": {"closed", "open"},
            "closed": set(),
        }

        if requested_status not in allowed_transitions.get(ticket.status, set()):
            raise TicketStatusTransitionError(
                f"Cannot change ticket status from '{ticket.status}' "
                f"to '{requested_status}'."
            )

        # Preserve the resolution timestamp when closing a resolved ticket.
        # Clear it when reopening the ticket.
        resolved_at = (
            None if requested_status == "open" else ticket.resolved_at
        )

        return self.ticket_repository.update_status(
            ticket=ticket,
            status=requested_status,
            resolved_at=resolved_at,
        )

    def assign_ticket(
        self,
        ticket_id: UUID,
        agent_id: UUID | None,
    ) -> Ticket | None:
        """Assign, reassign, or unassign a support ticket."""
        if agent_id is not None:
            agent = self.ticket_repository.get_active_support_agent(agent_id)

            if agent is None:
                raise InvalidSupportAgentError(
                    "The requested user is not an active support agent."
                )

        return self.ticket_repository.assign_agent(
            ticket_id=ticket_id,
            agent_id=agent_id,
        )


class InvalidSupportAgentError(Exception):
    """Raised when the requested assignee is not an eligible support agent."""
