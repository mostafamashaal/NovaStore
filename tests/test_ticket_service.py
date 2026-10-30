from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.models.ticket import Ticket
from src.repositories.ticket_repository import TicketRepository
from src.services.ticket_service import (
    InvalidSupportAgentError,
    TicketService,
    TicketStatusTransitionError,
)


@pytest.fixture
def ticket_service():
    repository = MagicMock(spec=TicketRepository)
    service = TicketService(repository)
    return service, repository


def make_ticket(status: str) -> Ticket:
    return Ticket(
        id=uuid4(),
        ticket_number="TKT-2026-00124",
        customer_id=uuid4(),
        category="shipping",
        priority="high",
        status=status,
        subject="Where is my order?",
        description="My order has not arrived.",
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
        resolved_at=(
            datetime(2026, 10, 17, tzinfo=timezone.utc)
            if status == "resolved"
            else None
        ),
    )


@pytest.mark.parametrize(
    ("current_status", "requested_status"),
    [
        ("open", "closed"),
        ("in_progress", "closed"),
        ("waiting_customer", "closed"),
        ("resolved", "closed"),
        ("resolved", "open"),
    ],
)
def test_update_ticket_status_allows_valid_transitions(
    ticket_service,
    current_status,
    requested_status,
):
    service, repository = ticket_service
    customer_id = uuid4()
    ticket = make_ticket(current_status)

    repository.get_by_id_for_customer.return_value = ticket
    repository.update_status.return_value = ticket

    result = service.update_ticket_status_for_customer(
        ticket_id=ticket.id,
        customer_id=customer_id,
        requested_status=requested_status,
    )

    assert result is ticket
    repository.get_by_id_for_customer.assert_called_once_with(
        ticket_id=ticket.id,
        customer_id=customer_id,
    )

    expected_resolved_at = (
        None if requested_status == "open" else ticket.resolved_at
    )
    repository.update_status.assert_called_once_with(
        ticket=ticket,
        status=requested_status,
        resolved_at=expected_resolved_at,
    )


@pytest.mark.parametrize(
    ("current_status", "requested_status"),
    [
        ("open", "open"),
        ("in_progress", "in_progress"),
        ("waiting_customer", "waiting_customer"),
        ("resolved", "resolved"),
        ("closed", "closed"),
        ("closed", "open"),
        ("open", "resolved"),
    ],
)
def test_update_ticket_status_rejects_invalid_transitions(
    ticket_service,
    current_status,
    requested_status,
):
    service, repository = ticket_service
    ticket = make_ticket(current_status)
    repository.get_by_id_for_customer.return_value = ticket

    with pytest.raises(TicketStatusTransitionError):
        service.update_ticket_status_for_customer(
            ticket_id=ticket.id,
            customer_id=ticket.customer_id,
            requested_status=requested_status,
        )

    repository.update_status.assert_not_called()


def test_update_ticket_status_returns_none_for_missing_or_unowned_ticket(
    ticket_service,
):
    service, repository = ticket_service
    repository.get_by_id_for_customer.return_value = None

    result = service.update_ticket_status_for_customer(
        ticket_id=uuid4(),
        customer_id=uuid4(),
        requested_status="closed",
    )

    assert result is None
    repository.update_status.assert_not_called()


def test_assign_ticket_accepts_active_support_agent(ticket_service):
    service, repository = ticket_service
    ticket_id = uuid4()
    agent_id = uuid4()
    agent = MagicMock()
    ticket = make_ticket("open")

    repository.get_active_support_agent.return_value = agent
    repository.assign_agent.return_value = ticket

    result = service.assign_ticket(ticket_id, agent_id)

    assert result is ticket
    repository.get_active_support_agent.assert_called_once_with(agent_id)
    repository.assign_agent.assert_called_once_with(
        ticket_id=ticket_id,
        agent_id=agent_id,
    )


def test_assign_ticket_rejects_ineligible_agent(ticket_service):
    service, repository = ticket_service
    repository.get_active_support_agent.return_value = None

    with pytest.raises(InvalidSupportAgentError):
        service.assign_ticket(uuid4(), uuid4())

    repository.assign_agent.assert_not_called()


def test_assign_ticket_allows_unassignment_without_agent_validation(
    ticket_service,
):
    service, repository = ticket_service
    ticket_id = uuid4()
    ticket = make_ticket("open")
    repository.assign_agent.return_value = ticket

    result = service.assign_ticket(ticket_id, None)

    assert result is ticket
    repository.get_active_support_agent.assert_not_called()
    repository.assign_agent.assert_called_once_with(
        ticket_id=ticket_id,
        agent_id=None,
    )


def test_assign_ticket_returns_none_when_ticket_is_missing(ticket_service):
    service, repository = ticket_service
    agent_id = uuid4()
    repository.get_active_support_agent.return_value = MagicMock()
    repository.assign_agent.return_value = None

    result = service.assign_ticket(uuid4(), agent_id)

    assert result is None
