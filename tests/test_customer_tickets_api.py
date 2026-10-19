from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user


@pytest.fixture
def customer_tickets_api_client():
    db = MagicMock()
    original_db_override = app.dependency_overrides.get(get_db)

    def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client, db
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override


def make_user():
    return SimpleNamespace(
        id=uuid4(),
        email="customer@example.com",
        role="customer",
        is_active=True,
        password_hash="test-password-hash",
    )


def make_customer(user_id):
    return SimpleNamespace(
        id=uuid4(),
        user_id=user_id,
        first_name="Test",
        last_name="Customer",
        phone=None,
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
    )


def make_ticket(customer_id, ticket_number="TKT-2026-00124"):
    return SimpleNamespace(
        id=uuid4(),
        ticket_number=ticket_number,
        customer_id=customer_id,
        conversation_id=uuid4(),
        assigned_agent_id=uuid4(),
        category="shipping",
        priority="high",
        status="open",
        subject="Where is my order?",
        description="My order has not arrived yet.",
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
        resolved_at=None,
    )


@pytest.fixture
def authenticated_customer_tickets(customer_tickets_api_client):
    client, db = customer_tickets_api_client
    user = make_user()
    customer = make_customer(user.id)

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        yield client, db, user, customer
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override


def test_list_my_tickets_returns_only_public_ticket_fields(
    authenticated_customer_tickets,
):
    client, db, user, customer = authenticated_customer_tickets
    ticket = make_ticket(customer.id)

    db.scalar.return_value = customer
    db.scalars.return_value.all.return_value = [ticket]

    response = client.get("/customers/me/tickets")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "category": "shipping",
            "priority": "high",
            "status": "open",
            "subject": "Where is my order?",
            "description": "My order has not arrived yet.",
            "created_at": "2026-10-15T00:00:00Z",
            "updated_at": "2026-10-16T00:00:00Z",
            "resolved_at": None,
        }
    ]

    data = response.json()[0]
    assert "customer_id" not in data
    assert "assigned_agent_id" not in data
    assert "conversation_id" not in data

    statement = db.scalars.call_args.args[0]
    assert customer.id in statement.compile().params.values()


def test_list_my_tickets_returns_empty_list_when_customer_has_no_tickets(
    authenticated_customer_tickets,
):
    client, db, user, customer = authenticated_customer_tickets

    db.scalar.return_value = customer
    db.scalars.return_value.all.return_value = []

    response = client.get("/customers/me/tickets")

    assert response.status_code == 200
    assert response.json() == []


def test_list_my_tickets_returns_404_when_customer_profile_is_missing(
    authenticated_customer_tickets,
):
    client, db, user, customer = authenticated_customer_tickets

    db.scalar.return_value = None

    response = client.get("/customers/me/tickets")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"
    db.scalars.assert_not_called()


def test_list_my_tickets_requires_authentication(
    customer_tickets_api_client,
):
    client, db = customer_tickets_api_client

    response = client.get("/customers/me/tickets")

    assert response.status_code == 401
    db.scalar.assert_not_called()
    db.scalars.assert_not_called()


def test_get_my_ticket_returns_ticket_details(
    authenticated_customer_tickets,
):
    client, db, user, customer = authenticated_customer_tickets
    ticket = make_ticket(customer.id)

    db.scalar.side_effect = [customer, ticket]

    response = client.get(f"/customers/me/tickets/{ticket.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(ticket.id)
    assert data["ticket_number"] == ticket.ticket_number
    assert data["category"] == "shipping"
    assert data["priority"] == "high"
    assert data["status"] == "open"
    assert data["subject"] == "Where is my order?"
    assert data["resolved_at"] is None

    assert "customer_id" not in data
    assert "assigned_agent_id" not in data
    assert "conversation_id" not in data

    statement = db.scalar.call_args.args[0]
    parameters = statement.compile().params.values()
    assert ticket.id in parameters
    assert customer.id in parameters


def test_get_my_ticket_returns_404_for_another_customers_ticket(
    authenticated_customer_tickets,
):
    client, db, user, customer = authenticated_customer_tickets
    ticket = make_ticket(customer_id=uuid4())

    db.scalar.side_effect = [customer, None]

    response = client.get(f"/customers/me/tickets/{ticket.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_get_my_ticket_returns_404_when_ticket_does_not_exist(
    authenticated_customer_tickets,
):
    client, db, user, customer = authenticated_customer_tickets

    db.scalar.side_effect = [customer, None]

    response = client.get(f"/customers/me/tickets/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_get_my_ticket_returns_404_when_customer_profile_is_missing(
    authenticated_customer_tickets,
):
    client, db, user, customer = authenticated_customer_tickets

    db.scalar.return_value = None

    response = client.get(f"/customers/me/tickets/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"


def test_get_my_ticket_requires_authentication(
    customer_tickets_api_client,
):
    client, db = customer_tickets_api_client

    response = client.get(f"/customers/me/tickets/{uuid4()}")

    assert response.status_code == 401
    db.scalar.assert_not_called()
