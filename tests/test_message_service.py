from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.services.message_service import (
    MessageService,
    TicketReplyNotAllowedError,
)


@pytest.fixture
def repositories():
    message_repository = MagicMock()
    ticket_repository = MagicMock()

    service = MessageService(
        message_repository=message_repository,
        ticket_repository=ticket_repository,
    )

    return service, message_repository, ticket_repository


def test_list_messages_returns_empty_list_without_conversation(repositories):
    service, message_repository, ticket_repository = repositories
    ticket_id = uuid4()
    customer_id = uuid4()

    ticket_repository.get_by_id_for_customer.return_value = MagicMock(
        conversation_id=None
    )

    result = service.list_messages_for_ticket(
        ticket_id=ticket_id,
        customer_id=customer_id,
    )

    assert result == []
    message_repository.list_by_conversation.assert_not_called()


def test_list_messages_returns_none_for_unowned_ticket(repositories):
    service, message_repository, ticket_repository = repositories
    ticket_repository.get_by_id_for_customer.return_value = None

    result = service.list_messages_for_ticket(
        ticket_id=uuid4(),
        customer_id=uuid4(),
    )

    assert result is None
    message_repository.list_by_conversation.assert_not_called()


def test_list_messages_uses_ticket_conversation(repositories):
    service, message_repository, ticket_repository = repositories
    conversation_id = uuid4()
    expected_messages = [MagicMock(), MagicMock()]

    ticket_repository.get_by_id_for_customer.return_value = MagicMock(
        conversation_id=conversation_id
    )
    message_repository.list_by_conversation.return_value = expected_messages

    result = service.list_messages_for_ticket(
        ticket_id=uuid4(),
        customer_id=uuid4(),
    )

    assert result == expected_messages
    message_repository.list_by_conversation.assert_called_once_with(
        conversation_id=conversation_id
    )


def test_create_customer_reply_delegates_to_repository(repositories):
    service, message_repository, _ = repositories
    expected_message = MagicMock()
    message_repository.create_customer_reply.return_value = expected_message

    ticket_id = uuid4()
    customer_id = uuid4()
    sender_user_id = uuid4()

    result = service.create_customer_reply(
        ticket_id=ticket_id,
        customer_id=customer_id,
        sender_user_id=sender_user_id,
        content="Please help with my order.",
    )

    assert result is expected_message
    message_repository.create_customer_reply.assert_called_once_with(
        ticket_id=ticket_id,
        customer_id=customer_id,
        sender_user_id=sender_user_id,
        content="Please help with my order.",
    )


def test_create_customer_reply_translates_value_error(repositories):
    service, message_repository, _ = repositories
    message_repository.create_customer_reply.side_effect = ValueError(
        "Customers cannot reply to resolved or closed tickets."
    )

    with pytest.raises(TicketReplyNotAllowedError):
        service.create_customer_reply(
            ticket_id=uuid4(),
            customer_id=uuid4(),
            sender_user_id=uuid4(),
            content="I have another question.",
        )
