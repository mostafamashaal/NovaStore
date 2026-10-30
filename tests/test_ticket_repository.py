from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.models.ticket import Ticket
from src.models.user import User
from src.repositories.ticket_repository import TicketRepository


def make_repository():
    """Create a ticket repository with a mocked SQLAlchemy session."""
    session = MagicMock()
    repository = TicketRepository(session)
    return repository, session


def test_create_generates_ticket_number_and_persists_ticket(monkeypatch):
    repository, session = make_repository()
    customer_id = uuid4()

    # Simulate PostgreSQL returning the next sequence value.
    session.execute.return_value.scalar_one.return_value = 128

    # Freeze the year so the expected ticket number is deterministic.
    fixed_now = datetime(2026, 10, 19, tzinfo=timezone.utc)

    class FixedDateTime:
        @staticmethod
        def now(tz=None):
            assert tz == timezone.utc
            return fixed_now

    monkeypatch.setattr(
        "src.repositories.ticket_repository.datetime",
        FixedDateTime,
    )

    ticket = repository.create(
        customer_id=customer_id,
        category="shipping",
        priority="high",
        subject="Where is my order?",
        description="My order has not arrived yet.",
    )

    assert isinstance(ticket, Ticket)
    assert ticket.id is not None
    assert ticket.ticket_number == "TKT-2026-00128"
    assert ticket.customer_id == customer_id
    assert ticket.category == "shipping"
    assert ticket.priority == "high"
    assert ticket.status == "open"
    assert ticket.subject == "Where is my order?"
    assert ticket.description == "My order has not arrived yet."

    session.execute.assert_called_once()
    session.add.assert_called_once_with(ticket)
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(ticket)
    session.rollback.assert_not_called()


def test_create_rolls_back_when_commit_fails(monkeypatch):
    repository, session = make_repository()
    session.execute.return_value.scalar_one.return_value = 129
    session.commit.side_effect = RuntimeError("Database commit failed")

    with pytest.raises(RuntimeError, match="Database commit failed"):
        repository.create(
            customer_id=uuid4(),
            category="technical",
            priority="medium",
            subject="Application issue",
            description="The application stops responding.",
        )

    session.add.assert_called_once()
    session.commit.assert_called_once_with()
    session.rollback.assert_called_once_with()
    session.refresh.assert_not_called()


def test_create_rolls_back_when_refresh_fails(monkeypatch):
    repository, session = make_repository()
    session.execute.return_value.scalar_one.return_value = 130
    session.refresh.side_effect = RuntimeError("Database refresh failed")

    with pytest.raises(RuntimeError, match="Database refresh failed"):
        repository.create(
            customer_id=uuid4(),
            category="complaint",
            priority="low",
            subject="Delivery complaint",
            description="The delivery was delayed.",
        )

    session.add.assert_called_once()
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once()
    session.rollback.assert_called_once_with()

def test_create_rolls_back_when_sequence_lookup_fails():
    repository, session = make_repository()
    session.execute.side_effect = RuntimeError(
        "Sequence lookup failed"
    )

    with pytest.raises(RuntimeError, match="Sequence lookup failed"):
        repository.create(
            customer_id=uuid4(),
            category="technical",
            priority="medium",
            subject="Application issue",
            description="The application stops responding.",
        )

    session.execute.assert_called_once()
    session.rollback.assert_called_once_with()
    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_get_active_support_agent_returns_eligible_agent():
    repository, session = make_repository()
    agent = MagicMock(spec=User)
    agent_id = uuid4()
    session.scalar.return_value = agent

    result = repository.get_active_support_agent(agent_id)

    assert result is agent
    session.scalar.assert_called_once()


def test_get_active_support_agent_returns_none_when_ineligible():
    repository, session = make_repository()
    session.scalar.return_value = None

    result = repository.get_active_support_agent(uuid4())

    assert result is None
    session.scalar.assert_called_once()


def test_assign_agent_persists_assignment():
    repository, session = make_repository()
    ticket = MagicMock(spec=Ticket)
    ticket.assigned_agent_id = None
    ticket_id = uuid4()
    agent_id = uuid4()
    session.scalar.return_value = ticket

    result = repository.assign_agent(ticket_id, agent_id)

    assert result is ticket
    assert ticket.assigned_agent_id == agent_id
    assert ticket.updated_at is not None
    session.scalar.assert_called_once()
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(ticket)
    session.rollback.assert_not_called()


def test_assign_agent_can_unassign_ticket():
    repository, session = make_repository()
    ticket = MagicMock(spec=Ticket)
    ticket.assigned_agent_id = uuid4()
    session.scalar.return_value = ticket

    result = repository.assign_agent(ticket.id, None)

    assert result is ticket
    assert ticket.assigned_agent_id is None
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(ticket)


def test_assign_agent_returns_none_when_ticket_does_not_exist():
    repository, session = make_repository()
    session.scalar.return_value = None

    result = repository.assign_agent(uuid4(), uuid4())

    assert result is None
    session.commit.assert_not_called()
    session.refresh.assert_not_called()
    session.rollback.assert_not_called()


def test_assign_agent_rolls_back_when_commit_fails():
    repository, session = make_repository()
    ticket = MagicMock(spec=Ticket)
    session.scalar.return_value = ticket
    session.commit.side_effect = RuntimeError("Database commit failed")

    with pytest.raises(RuntimeError, match="Database commit failed"):
        repository.assign_agent(uuid4(), uuid4())

    session.commit.assert_called_once_with()
    session.rollback.assert_called_once_with()
    session.refresh.assert_not_called()
