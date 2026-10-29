from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user
from src.repositories.ticket_repository import TicketRepository


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


def test_create_my_ticket_returns_created_ticket(
    authenticated_customer_tickets,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_tickets
    created_records = []

    def fake_create(
        repository,
        customer_id,
        category,
        priority,
        subject,
        description,
    ):
        created_records.append(
            {
                "customer_id": customer_id,
                "category": category,
                "priority": priority,
                "subject": subject,
                "description": description,
            }
        )
        return SimpleNamespace(
            id=uuid4(),
            ticket_number="TKT-2026-00128",
            category=category,
            priority=priority,
            status="open",
            subject=subject,
            description=description,
            created_at=datetime(2026, 10, 19, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 19, tzinfo=timezone.utc),
            resolved_at=None,
        )

    monkeypatch.setattr(TicketRepository, "create", fake_create)
    db.scalar.return_value = customer

    response = client.post(
        "/customers/me/tickets",
        json={
            "category": "shipping",
            "priority": "high",
            "subject": "Where is my order?",
            "description": "My order has not arrived yet.",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["ticket_number"] == "TKT-2026-00128"
    assert data["category"] == "shipping"
    assert data["priority"] == "high"
    assert data["status"] == "open"
    assert data["subject"] == "Where is my order?"
    assert data["description"] == "My order has not arrived yet."
    assert data["resolved_at"] is None

    assert "customer_id" not in data
    assert "assigned_agent_id" not in data
    assert "conversation_id" not in data

    assert created_records == [
        {
            "customer_id": customer.id,
            "category": "shipping",
            "priority": "high",
            "subject": "Where is my order?",
            "description": "My order has not arrived yet.",
        }
    ]


def test_create_my_ticket_defaults_priority_to_medium(
    authenticated_customer_tickets,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_tickets
    captured = {}

    def fake_create(
        repository,
        customer_id,
        category,
        priority,
        subject,
        description,
    ):
        captured["customer_id"] = customer_id
        captured["priority"] = priority

        return SimpleNamespace(
            id=uuid4(),
            ticket_number="TKT-2026-00128",
            category=category,
            priority=priority,
            status="open",
            subject=subject,
            description=description,
            created_at=datetime(2026, 10, 19, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 19, tzinfo=timezone.utc),
            resolved_at=None,
        )

    monkeypatch.setattr(TicketRepository, "create", fake_create)
    db.scalar.return_value = customer

    response = client.post(
        "/customers/me/tickets",
        json={
            "category": "technical",
            "subject": "App issue",
            "description": "The application stops responding.",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "medium"
    assert captured == {
        "customer_id": customer.id,
        "priority": "medium",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {
            "category": "invalid_category",
            "subject": "Help",
            "description": "I need help.",
        },
        {
            "category": "shipping",
            "priority": "critical",
            "subject": "Help",
            "description": "I need help.",
        },
        {
            "category": "shipping",
            "subject": "   ",
            "description": "I need help.",
        },
        {
            "category": "shipping",
            "subject": "x" * 256,
            "description": "I need help.",
        },
        {
            "category": "shipping",
            "subject": "Help",
            "description": "   ",
        },
        {
            "category": "shipping",
            "subject": "Help",
            "description": "x" * 5001,
        },
    ],
)
def test_create_my_ticket_rejects_invalid_input(
    authenticated_customer_tickets,
    payload,
):
    client, db, user, customer = authenticated_customer_tickets

    response = client.post("/customers/me/tickets", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "extra_field",
    [
        {"customer_id": str(uuid4())},
        {"status": "resolved"},
        {"assigned_agent_id": str(uuid4())},
        {"ticket_number": "TKT-2026-99999"},
    ],
)
def test_create_my_ticket_rejects_privileged_extra_fields(
    authenticated_customer_tickets,
    extra_field,
):
    client, db, user, customer = authenticated_customer_tickets

    payload = {
        "category": "shipping",
        "subject": "Where is my order?",
        "description": "My order has not arrived yet.",
        **extra_field,
    }

    response = client.post("/customers/me/tickets", json=payload)

    assert response.status_code == 422


def test_create_my_ticket_returns_404_when_customer_profile_is_missing(
    authenticated_customer_tickets,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_tickets
    db.scalar.return_value = None
    create_mock = MagicMock()
    monkeypatch.setattr(TicketRepository, "create", create_mock)

    response = client.post(
        "/customers/me/tickets",
        json={
            "category": "shipping",
            "subject": "Where is my order?",
            "description": "My order has not arrived yet.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"
    create_mock.assert_not_called()


def test_create_my_ticket_requires_authentication(
    customer_tickets_api_client,
):
    client, db = customer_tickets_api_client

    response = client.post(
        "/customers/me/tickets",
        json={
            "category": "shipping",
            "subject": "Where is my order?",
            "description": "My order has not arrived yet.",
        },
    )

    assert response.status_code == 401
    db.scalar.assert_not_called()


@pytest.mark.parametrize(
    ("current_status", "requested_status", "expected_status"),
    [
        ("open", "closed", 200),
        ("in_progress", "closed", 200),
        ("waiting_customer", "closed", 200),
        ("resolved", "closed", 200),
        ("resolved", "open", 200),
    ],
)
def test_update_my_ticket_status_returns_updated_ticket(
    authenticated_customer_tickets,
    monkeypatch,
    current_status,
    requested_status,
    expected_status,
):
    client, db, user, customer = authenticated_customer_tickets
    ticket = make_ticket(customer.id)
    ticket.status = current_status

    if current_status == "resolved":
        ticket.resolved_at = datetime(2026, 10, 17, tzinfo=timezone.utc)

    db.scalar.return_value = customer

    def fake_update_status(
        repository,
        *,
        ticket_id,
        customer_id,
        requested_status,
    ):
        assert ticket_id == ticket.id
        assert customer_id == customer.id
        assert requested_status in {"open", "closed"}

        ticket.status = requested_status
        if requested_status == "open":
            ticket.resolved_at = None
        ticket.updated_at = datetime(2026, 10, 20, tzinfo=timezone.utc)
        return ticket

    monkeypatch.setattr(
        "src.services.ticket_service.TicketService."
        "update_ticket_status_for_customer",
        fake_update_status,
    )

    response = client.patch(
        f"/customers/me/tickets/{ticket.id}/status",
        json={"status": requested_status},
    )

    assert response.status_code == expected_status
    assert response.json()["status"] == requested_status
    assert response.json()["updated_at"] == "2026-10-20T00:00:00Z"

    if requested_status == "open":
        assert response.json()["resolved_at"] is None


@pytest.mark.parametrize("invalid_status", ["in_progress", "waiting_customer", "resolved"])
def test_update_my_ticket_status_rejects_internal_statuses(
    authenticated_customer_tickets,
    invalid_status,
):
    client, db, user, customer = authenticated_customer_tickets
    db.scalar.return_value = customer

    response = client.patch(
        f"/customers/me/tickets/{uuid4()}/status",
        json={"status": invalid_status},
    )

    assert response.status_code == 422


def test_update_my_ticket_status_returns_409_for_invalid_transition(
    authenticated_customer_tickets,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_tickets
    ticket = make_ticket(customer.id)
    ticket.status = "closed"
    db.scalar.return_value = customer

    def fake_update_status(
        service,
        *,
        ticket_id,
        customer_id,
        requested_status,
    ):
        from src.services.ticket_service import TicketStatusTransitionError

        raise TicketStatusTransitionError(
            "Cannot change ticket status from 'closed' to 'open'."
        )

    monkeypatch.setattr(
        "src.services.ticket_service.TicketService."
        "update_ticket_status_for_customer",
        fake_update_status,
    )

    response = client.patch(
        f"/customers/me/tickets/{ticket.id}/status",
        json={"status": "open"},
    )

    assert response.status_code == 409


def test_update_my_ticket_status_returns_404_for_missing_ticket(
    authenticated_customer_tickets,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_tickets
    db.scalar.return_value = customer

    monkeypatch.setattr(
        "src.services.ticket_service.TicketService."
        "update_ticket_status_for_customer",
        lambda service, **kwargs: None,
    )

    response = client.patch(
        f"/customers/me/tickets/{uuid4()}/status",
        json={"status": "closed"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_update_my_ticket_status_requires_authentication(
    customer_tickets_api_client,
):
    client, db = customer_tickets_api_client

    response = client.patch(
        f"/customers/me/tickets/{uuid4()}/status",
        json={"status": "closed"},
    )

    assert response.status_code == 401
