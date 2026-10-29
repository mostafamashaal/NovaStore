
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user
from src.repositories.message_repository import MessageRepository
from src.repositories.ticket_repository import TicketRepository


@pytest.fixture
def customer_ticket_messages_api_client():
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


def make_ticket(customer_id, status="open", conversation_id=None):
    return SimpleNamespace(
        id=uuid4(),
        ticket_number="TKT-2026-00124",
        customer_id=customer_id,
        conversation_id=conversation_id,
        assigned_agent_id=None,
        category="shipping",
        priority="high",
        status=status,
        subject="Where is my order?",
        description="My order has not arrived yet.",
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
        resolved_at=None,
    )


def make_message(
    conversation_id,
    *,
    sender_type="customer",
    content="Could you provide an update?",
):
    return SimpleNamespace(
        id=uuid4(),
        conversation_id=conversation_id,
        sender_type=sender_type,
        sender_user_id=uuid4(),
        content=content,
        created_at=datetime(2026, 10, 20, 10, 30, tzinfo=timezone.utc),
    )


@pytest.fixture
def authenticated_customer_ticket_messages(
    customer_ticket_messages_api_client,
):
    client, db = customer_ticket_messages_api_client
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


def test_list_ticket_messages_returns_public_message_fields(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    conversation_id = uuid4()
    ticket = make_ticket(customer.id, conversation_id=conversation_id)
    message = make_message(conversation_id)

    db.scalar.return_value = customer

    def fake_get_ticket(repository, *, ticket_id, customer_id):
        assert ticket_id == ticket.id
        assert customer_id == customer.id
        return ticket

    expected_conversation_id = conversation_id

    def fake_list_messages(repository, *, conversation_id):
        assert conversation_id == expected_conversation_id
        return [message]

    monkeypatch.setattr(
        TicketRepository,
        "get_by_id_for_customer",
        fake_get_ticket,
    )
    monkeypatch.setattr(
        MessageRepository,
        "list_by_conversation",
        fake_list_messages,
    )

    response = client.get(
        f"/customers/me/tickets/{ticket.id}/messages"
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(message.id),
            "sender_type": "customer",
            "content": "Could you provide an update?",
            "created_at": "2026-10-20T10:30:00Z",
        }
    ]

    data = response.json()[0]
    assert "sender_user_id" not in data
    assert "conversation_id" not in data


def test_list_ticket_messages_returns_empty_list_without_conversation(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    ticket = make_ticket(customer.id, conversation_id=None)

    db.scalar.return_value = customer

    monkeypatch.setattr(
        TicketRepository,
        "get_by_id_for_customer",
        lambda repository, *, ticket_id, customer_id: ticket,
    )
    list_messages_mock = MagicMock()
    monkeypatch.setattr(
        MessageRepository,
        "list_by_conversation",
        list_messages_mock,
    )

    response = client.get(
        f"/customers/me/tickets/{ticket.id}/messages"
    )

    assert response.status_code == 200
    assert response.json() == []
    list_messages_mock.assert_not_called()


def test_list_ticket_messages_returns_404_for_missing_or_unowned_ticket(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    db.scalar.return_value = customer

    monkeypatch.setattr(
        TicketRepository,
        "get_by_id_for_customer",
        lambda repository, *, ticket_id, customer_id: None,
    )

    response = client.get(
        f"/customers/me/tickets/{uuid4()}/messages"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_list_ticket_messages_returns_404_when_customer_profile_is_missing(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    db.scalar.return_value = None

    list_messages_mock = MagicMock()
    monkeypatch.setattr(
        MessageRepository,
        "list_by_conversation",
        list_messages_mock,
    )

    response = client.get(
        f"/customers/me/tickets/{uuid4()}/messages"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"
    list_messages_mock.assert_not_called()


def test_list_ticket_messages_requires_authentication(
    customer_ticket_messages_api_client,
):
    client, db = customer_ticket_messages_api_client

    response = client.get(
        f"/customers/me/tickets/{uuid4()}/messages"
    )

    assert response.status_code == 401
    db.scalar.assert_not_called()


def test_create_ticket_message_returns_created_message(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    ticket_id = uuid4()
    conversation_id = uuid4()
    message = make_message(
        conversation_id,
        content="Thank you for the update.",
    )
    captured = {}

    db.scalar.return_value = customer

    def fake_create_reply(
        repository,
        *,
        ticket_id,
        customer_id,
        sender_user_id,
        content,
    ):
        captured.update(
            {
                "ticket_id": ticket_id,
                "customer_id": customer_id,
                "sender_user_id": sender_user_id,
                "content": content,
            }
        )
        return message

    monkeypatch.setattr(
        MessageRepository,
        "create_customer_reply",
        fake_create_reply,
    )

    response = client.post(
        f"/customers/me/tickets/{ticket_id}/messages",
        json={"content": "Thank you for the update."},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": str(message.id),
        "sender_type": "customer",
        "content": "Thank you for the update.",
        "created_at": "2026-10-20T10:30:00Z",
    }

    assert captured == {
        "ticket_id": ticket_id,
        "customer_id": customer.id,
        "sender_user_id": user.id,
        "content": "Thank you for the update.",
    }

    assert "sender_user_id" not in response.json()
    assert "conversation_id" not in response.json()


def test_create_ticket_message_returns_404_for_missing_or_unowned_ticket(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    db.scalar.return_value = customer

    monkeypatch.setattr(
        MessageRepository,
        "create_customer_reply",
        lambda repository, **kwargs: None,
    )

    response = client.post(
        f"/customers/me/tickets/{uuid4()}/messages",
        json={"content": "Any update?"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_create_ticket_message_returns_409_for_closed_ticket(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    db.scalar.return_value = customer

    def fake_create_reply(repository, **kwargs):
        raise ValueError(
            "Customers cannot reply to resolved or closed tickets."
        )

    monkeypatch.setattr(
        MessageRepository,
        "create_customer_reply",
        fake_create_reply,
    )

    response = client.post(
        f"/customers/me/tickets/{uuid4()}/messages",
        json={"content": "I have another question."},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Customers cannot reply to resolved or closed tickets."
    )


def test_create_ticket_message_returns_404_when_customer_profile_is_missing(
    authenticated_customer_ticket_messages,
    monkeypatch,
):
    client, db, user, customer = authenticated_customer_ticket_messages
    db.scalar.return_value = None

    create_reply_mock = MagicMock()
    monkeypatch.setattr(
        MessageRepository,
        "create_customer_reply",
        create_reply_mock,
    )

    response = client.post(
        f"/customers/me/tickets/{uuid4()}/messages",
        json={"content": "Any update?"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"
    create_reply_mock.assert_not_called()


def test_create_ticket_message_requires_authentication(
    customer_ticket_messages_api_client,
):
    client, db = customer_ticket_messages_api_client

    response = client.post(
        f"/customers/me/tickets/{uuid4()}/messages",
        json={"content": "Any update?"},
    )

    assert response.status_code == 401
    db.scalar.assert_not_called()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"content": ""},
        {"content": "   "},
        {"content": "x" * 5001},
        {"content": "Any update?", "sender_type": "support_agent"},
        {"content": "Any update?", "sender_user_id": str(uuid4())},
        {"content": "Any update?", "conversation_id": str(uuid4())},
    ],
)
def test_create_ticket_message_rejects_invalid_or_privileged_input(
    authenticated_customer_ticket_messages,
    payload,
):
    client, db, user, customer = authenticated_customer_ticket_messages

    response = client.post(
        f"/customers/me/tickets/{uuid4()}/messages",
        json=payload,
    )

    assert response.status_code == 422
