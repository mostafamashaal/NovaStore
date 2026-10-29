from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user
from src.services.message_service import (
    MessageService,
    TicketAgentReplyForbiddenError,
    TicketReplyNotAllowedError,
)


@pytest.fixture
def support_client():
    user = SimpleNamespace(
        id=uuid4(),
        role="support_agent",
        is_active=True,
    )
    db = MagicMock()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as client:
        yield client, user, db

    app.dependency_overrides.clear()


def make_message(content="I am checking your order."):
    return SimpleNamespace(
        id=uuid4(),
        sender_type="support_agent",
        content=content,
        created_at=datetime(2026, 10, 29, tzinfo=timezone.utc),
    )


def test_support_agent_can_reply_to_ticket(
    support_client, monkeypatch
):
    client, user, _ = support_client
    ticket_id = uuid4()
    message = make_message()

    def fake_reply(self, **kwargs):
        assert kwargs["ticket_id"] == ticket_id
        assert kwargs["sender_user_id"] == user.id
        assert kwargs["sender_role"] == "support_agent"
        assert kwargs["content"] == message.content
        return message

    monkeypatch.setattr(
        MessageService,
        "create_support_agent_reply",
        fake_reply,
    )

    response = client.post(
        f"/support/tickets/{ticket_id}/messages",
        json={"content": message.content},
    )

    assert response.status_code == 201
    assert response.json()["sender_type"] == "support_agent"
    assert response.json()["content"] == message.content


def test_unassigned_agent_gets_forbidden_response(
    support_client, monkeypatch
):
    client, _, _ = support_client

    def fake_reply(self, **kwargs):
        raise TicketAgentReplyForbiddenError(
            "Support agents can reply only to tickets assigned to them."
        )

    monkeypatch.setattr(
        MessageService,
        "create_support_agent_reply",
        fake_reply,
    )

    response = client.post(
        f"/support/tickets/{uuid4()}/messages",
        json={"content": "Checking this for you."},
    )

    assert response.status_code == 403


def test_resolved_ticket_rejects_agent_reply(
    support_client, monkeypatch
):
    client, _, _ = support_client

    def fake_reply(self, **kwargs):
        raise TicketReplyNotAllowedError(
            "Support agents cannot reply to resolved or closed tickets."
        )

    monkeypatch.setattr(
        MessageService,
        "create_support_agent_reply",
        fake_reply,
    )

    response = client.post(
        f"/support/tickets/{uuid4()}/messages",
        json={"content": "Following up."},
    )

    assert response.status_code == 409


def test_missing_ticket_returns_not_found(
    support_client, monkeypatch
):
    client, _, _ = support_client

    monkeypatch.setattr(
        MessageService,
        "create_support_agent_reply",
        lambda self, **kwargs: None,
    )

    response = client.post(
        f"/support/tickets/{uuid4()}/messages",
        json={"content": "Following up."},
    )

    assert response.status_code == 404


def test_invalid_message_content_is_rejected(support_client):
    client, _, _ = support_client

    response = client.post(
        f"/support/tickets/{uuid4()}/messages",
        json={"content": "   "},
    )

    assert response.status_code == 422


def test_customer_cannot_supply_sender_identity(
    support_client
):
    client, _, _ = support_client

    response = client.post(
        f"/support/tickets/{uuid4()}/messages",
        json={
            "content": "Hello",
            "sender_type": "admin",
            "sender_user_id": str(uuid4()),
        },
    )

    assert response.status_code == 422
