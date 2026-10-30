from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user
from src.services.ticket_service import (
    InvalidSupportAgentError,
    TicketService,
)


@pytest.fixture
def assignment_client():
    user = SimpleNamespace(
        id=uuid4(),
        role="admin",
        is_active=True,
    )
    db = MagicMock()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as client:
        yield client, user

    app.dependency_overrides.clear()


def make_assigned_ticket(agent_id=None):
    return SimpleNamespace(
        id=uuid4(),
        ticket_number="TKT-2026-00124",
        assigned_agent_id=agent_id,
        updated_at=datetime.now(timezone.utc),
    )


def test_admin_can_assign_ticket(assignment_client, monkeypatch):
    client, _ = assignment_client
    expected_ticket_id = uuid4()
    expected_agent_id = uuid4()
    ticket = make_assigned_ticket(expected_agent_id)

    def fake_assign(self, ticket_id, agent_id):
        assert ticket_id == expected_ticket_id
        assert agent_id == expected_agent_id
        return ticket

    monkeypatch.setattr(TicketService, "assign_ticket", fake_assign)

    response = client.patch(
        f"/support/tickets/{expected_ticket_id}/assignment",
        json={"agent_id": str(expected_agent_id)},
    )

    assert response.status_code == 200
    assert response.json()["assigned_agent_id"] == str(expected_agent_id)
    assert response.json()["ticket_number"] == ticket.ticket_number


def test_admin_can_unassign_ticket(assignment_client, monkeypatch):
    client, _ = assignment_client
    expected_ticket_id = uuid4()

    # Simulate the ticket after successful unassignment.
    ticket = make_assigned_ticket()
    ticket.assigned_agent_id = None

    def fake_assign(self, ticket_id, agent_id):
        assert ticket_id == expected_ticket_id
        assert agent_id is None
        return ticket

    monkeypatch.setattr(
        TicketService,
        "assign_ticket",
        fake_assign,
    )

    response = client.patch(
        f"/support/tickets/{expected_ticket_id}/assignment",
        json={"agent_id": None},
    )

    assert response.status_code == 200
    assert response.json()["assigned_agent_id"] is None

@pytest.mark.parametrize("role", ["customer", "support_agent"])
def test_non_admin_cannot_assign_ticket(
    assignment_client,
    monkeypatch,
    role,
):
    client, user = assignment_client
    user.role = role

    def unexpected_call(*args, **kwargs):
        pytest.fail("Assignment service should not be called")

    monkeypatch.setattr(
        TicketService,
        "assign_ticket",
        unexpected_call,
    )

    response = client.patch(
        f"/support/tickets/{uuid4()}/assignment",
        json={"agent_id": str(uuid4())},
    )

    assert response.status_code == 403


def test_invalid_agent_returns_422(assignment_client, monkeypatch):
    client, _ = assignment_client

    def reject_agent(self, ticket_id, agent_id):
        raise InvalidSupportAgentError(
            "The requested user is not an active support agent."
        )

    monkeypatch.setattr(TicketService, "assign_ticket", reject_agent)

    response = client.patch(
        f"/support/tickets/{uuid4()}/assignment",
        json={"agent_id": str(uuid4())},
    )

    assert response.status_code == 422


def test_missing_ticket_returns_404(assignment_client, monkeypatch):
    client, _ = assignment_client

    monkeypatch.setattr(
        TicketService,
        "assign_ticket",
        lambda self, ticket_id, agent_id: None,
    )

    response = client.patch(
        f"/support/tickets/{uuid4()}/assignment",
        json={"agent_id": str(uuid4())},
    )

    assert response.status_code == 404


def test_assignment_requires_agent_id(assignment_client):
    client, _ = assignment_client

    response = client.patch(
        f"/support/tickets/{uuid4()}/assignment",
        json={},
    )

    assert response.status_code == 422
