from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.models.conversation import Conversation
from src.models.message import Message
from src.repositories.message_repository import MessageRepository


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def repository(db):
    return MessageRepository(db)


def test_list_by_conversation_returns_messages(db, repository):
    conversation_id = uuid4()
    expected_messages = [MagicMock(spec=Message), MagicMock(spec=Message)]

    db.scalars.return_value.all.return_value = expected_messages

    result = repository.list_by_conversation(conversation_id)

    assert result == expected_messages
    db.scalars.assert_called_once()
    db.scalars.return_value.all.assert_called_once()


def test_create_customer_reply_creates_conversation_and_message(
    db,
    repository,
):
    ticket_id = uuid4()
    customer_id = uuid4()
    sender_user_id = uuid4()

    ticket = MagicMock()
    ticket.id = ticket_id
    ticket.customer_id = customer_id
    ticket.status = "open"
    ticket.conversation_id = None

    db.scalars.return_value.first.return_value = ticket

    def flush_side_effect():
        # Simulate the database-generated timestamp after flushing a message.
        for call in db.add.call_args_list:
            instance = call.args[0]
            if isinstance(instance, Message) and instance.created_at is None:
                from datetime import datetime, timezone

                instance.created_at = datetime.now(timezone.utc)

    db.flush.side_effect = flush_side_effect

    result = repository.create_customer_reply(
        ticket_id=ticket_id,
        customer_id=customer_id,
        sender_user_id=sender_user_id,
        content="Please help with my order.",
    )

    added_objects = [call.args[0] for call in db.add.call_args_list]
    conversations = [
        item for item in added_objects if isinstance(item, Conversation)
    ]
    messages = [item for item in added_objects if isinstance(item, Message)]

    assert result is messages[0]
    assert len(conversations) == 1
    assert len(messages) == 1

    conversation = conversations[0]
    message = messages[0]

    assert conversation.customer_id == customer_id
    assert conversation.status == "open"
    assert ticket.conversation_id == conversation.id

    assert message.conversation_id == conversation.id
    assert message.sender_type == "customer"
    assert message.sender_user_id == sender_user_id
    assert message.content == "Please help with my order."

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(message)
    db.rollback.assert_not_called()


def test_create_customer_reply_returns_none_for_unowned_ticket(
    db,
    repository,
):
    db.scalars.return_value.first.return_value = None

    result = repository.create_customer_reply(
        ticket_id=uuid4(),
        customer_id=uuid4(),
        sender_user_id=uuid4(),
        content="Hello.",
    )

    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("ticket_status", ["resolved", "closed"])
def test_create_customer_reply_rejects_inactive_ticket(
    db,
    repository,
    ticket_status,
):
    ticket = MagicMock()
    ticket.status = ticket_status
    ticket.conversation_id = uuid4()

    db.scalars.return_value.first.return_value = ticket

    with pytest.raises(ValueError, match="resolved or closed"):
        repository.create_customer_reply(
            ticket_id=uuid4(),
            customer_id=uuid4(),
            sender_user_id=uuid4(),
            content="I need more help.",
        )

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_create_customer_reply_reuses_existing_conversation(
    db,
    repository,
):
    ticket_id = uuid4()
    customer_id = uuid4()
    sender_user_id = uuid4()
    conversation_id = uuid4()

    ticket = MagicMock()
    ticket.status = "open"
    ticket.conversation_id = conversation_id

    conversation = MagicMock(spec=Conversation)
    conversation.id = conversation_id
    conversation.customer_id = customer_id

    db.scalars.return_value.first.return_value = ticket
    db.get.return_value = conversation

    def flush_side_effect():
        for call in db.add.call_args_list:
            instance = call.args[0]
            if isinstance(instance, Message) and instance.created_at is None:
                from datetime import datetime, timezone

                instance.created_at = datetime.now(timezone.utc)

    db.flush.side_effect = flush_side_effect

    result = repository.create_customer_reply(
        ticket_id=ticket_id,
        customer_id=customer_id,
        sender_user_id=sender_user_id,
        content="Any update?",
    )

    added_objects = [call.args[0] for call in db.add.call_args_list]
    messages = [item for item in added_objects if isinstance(item, Message)]

    assert result is messages[0]
    assert len(messages) == 1
    assert not any(isinstance(item, Conversation) for item in added_objects)

    db.get.assert_called_once_with(Conversation, conversation_id)
    assert messages[0].conversation_id == conversation_id
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_create_customer_reply_rejects_another_customers_conversation(
    db,
    repository,
):
    customer_id = uuid4()
    conversation_id = uuid4()

    ticket = MagicMock()
    ticket.status = "open"
    ticket.conversation_id = conversation_id

    conversation = MagicMock(spec=Conversation)
    conversation.id = conversation_id
    conversation.customer_id = uuid4()

    db.scalars.return_value.first.return_value = ticket
    db.get.return_value = conversation

    with pytest.raises(
        RuntimeError,
        match="does not belong to this customer",
    ):
        repository.create_customer_reply(
            ticket_id=uuid4(),
            customer_id=customer_id,
            sender_user_id=uuid4(),
            content="Please help.",
        )

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_create_customer_reply_rejects_missing_linked_conversation(
    db,
    repository,
):
    ticket = MagicMock()
    ticket.status = "open"
    ticket.conversation_id = uuid4()

    db.scalars.return_value.first.return_value = ticket
    db.get.return_value = None

    with pytest.raises(
        RuntimeError,
        match="conversation that does not exist",
    ):
        repository.create_customer_reply(
            ticket_id=uuid4(),
            customer_id=uuid4(),
            sender_user_id=uuid4(),
            content="Please help.",
        )

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_create_customer_reply_rolls_back_when_message_flush_fails(
    db,
    repository,
):
    customer_id = uuid4()

    ticket = MagicMock()
    ticket.status = "open"
    ticket.conversation_id = None

    db.scalars.return_value.first.return_value = ticket
    db.flush.side_effect = [
        None,
        RuntimeError("Simulated message persistence failure"),
    ]

    with pytest.raises(
        RuntimeError,
        match="Simulated message persistence failure",
    ):
        repository.create_customer_reply(
            ticket_id=uuid4(),
            customer_id=customer_id,
            sender_user_id=uuid4(),
            content="Please help.",
        )

    added_objects = [call.args[0] for call in db.add.call_args_list]

    assert any(isinstance(item, Conversation) for item in added_objects)
    assert any(isinstance(item, Message) for item in added_objects)

    assert db.flush.call_count == 2
    db.commit.assert_not_called()
    db.rollback.assert_called_once()
