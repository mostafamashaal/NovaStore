from src.models.base import Base
from sqlalchemy import CheckConstraint
from src.models.user import User
from src.models.customer import Customer

from src.models.inventory import Inventory
from src.models.product import Product
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.order_status_history import OrderStatusHistory
from src.models.payment import Payment
from src.models.shipment import Shipment

from src.models.ticket import Ticket
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.refund import Refund
from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.models.agent_run import AgentRun
from src.models.tool_call import ToolCall
from sqlalchemy.dialects.postgresql import JSONB
from src.models.approval import Approval
from src.models.audit_log import AuditLog

def test_users_table_is_registered():
    assert "users" in Base.metadata.tables


def test_user_customer_relationship_is_scalar():
    assert User.customer.property.uselist is False


def test_customer_user_foreign_key():
    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Customer.__table__.foreign_keys
    }

    assert "users.id" in foreign_key_targets


def test_products_and_inventory_tables_are_registered():
    assert "products" in Base.metadata.tables
    assert "inventory" in Base.metadata.tables


def test_product_inventory_relationship_is_scalar():
    assert Product.inventory.property.uselist is False


def test_inventory_product_id_is_unique():
    assert Inventory.__table__.c.product_id.unique is True


def test_inventory_quantity_check_constraints():
    check_constraints = {
        constraint.name
        for constraint in Inventory.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "inventory_available_quantity_check" in check_constraints
    assert "inventory_reserved_quantity_check" in check_constraints


def test_orders_table_and_customer_foreign_key():
    assert "orders" in Base.metadata.tables

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Order.__table__.foreign_keys
    }

    assert "customers.id" in foreign_key_targets
    assert Order.__table__.c.order_number.unique is True


def test_order_status_and_amount_constraints():
    check_constraints = {
        constraint.name
        for constraint in Order.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "orders_status_check" in check_constraints
    assert "orders_total_amount_check" in check_constraints


def test_order_items_foreign_keys():
    assert "order_items" in Base.metadata.tables

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in OrderItem.__table__.foreign_keys
    }

    assert "orders.id" in foreign_key_targets
    assert "products.id" in foreign_key_targets


def test_order_item_quantity_and_price_constraints():
    check_constraints = {
        constraint.name
        for constraint in OrderItem.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "order_items_quantity_check" in check_constraints
    assert "order_items_unit_price_check" in check_constraints


def test_order_status_history_foreign_keys_and_constraint():
    assert "order_status_history" in Base.metadata.tables

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in OrderStatusHistory.__table__.foreign_keys
    }

    assert "orders.id" in foreign_key_targets
    assert "users.id" in foreign_key_targets

    check_constraints = {
        constraint.name
        for constraint in OrderStatusHistory.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert (
        "order_status_history_changed_by_type_check"
        in check_constraints
    )


def test_payment_foreign_key_and_amount_constraint():
    assert "payments" in Base.metadata.tables

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Payment.__table__.foreign_keys
    }

    assert "orders.id" in foreign_key_targets

    check_constraints = {
        constraint.name
        for constraint in Payment.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "payments_amount_check" in check_constraints


def test_order_history_and_payment_relationships():
    assert Order.status_history.property.uselist is True
    assert Order.payments.property.uselist is True

    assert OrderStatusHistory.order.property.back_populates == "status_history"
    assert Payment.order.property.back_populates == "payments"


def test_shipment_model():
    assert "shipments" in Base.metadata.tables

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Shipment.__table__.foreign_keys
    }

    assert "orders.id" in foreign_key_targets
    assert Shipment.order.property.uselist is False


def test_order_shipment_relationships():
    assert Order.shipments.property.uselist is True
    assert Shipment.order.property.uselist is False

    assert Order.shipments.property.back_populates == "order"
    assert Shipment.order.property.back_populates == "shipments"


def test_ticket_model():
    assert "tickets" in Base.metadata.tables

    assert Ticket.__table__.c.ticket_number.unique is True

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Ticket.__table__.foreign_keys
    }

    assert "customers.id" in foreign_key_targets
    assert "conversations.id" in foreign_key_targets
    assert "users.id" in foreign_key_targets

    check_constraint_names = {
        constraint.name
        for constraint in Ticket.__table__.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }

    assert "tickets_category_check" in check_constraint_names
    assert "tickets_priority_check" in check_constraint_names
    assert "tickets_status_check" in check_constraint_names



def test_ticket_conversation_relationship():
    from src.models.conversation import Conversation

    relationship = Ticket.conversation.property

    assert relationship.mapper.class_ is Conversation
    assert relationship.uselist is False
    assert relationship.local_columns == {Ticket.__table__.c.conversation_id}


def test_conversation_model():
    assert "conversations" in Base.metadata.tables

    assert list(Conversation.__table__.columns.keys()) == [
        "id",
        "customer_id",
        "status",
        "created_at",
        "updated_at",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Conversation.__table__.foreign_keys
    }

    assert "customers.id" in foreign_key_targets


def test_message_model():
    assert "messages" in Base.metadata.tables

    assert list(Message.__table__.columns.keys()) == [
        "id",
        "conversation_id",
        "sender_type",
        "sender_user_id",
        "content",
        "created_at",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Message.__table__.foreign_keys
    }

    assert "conversations.id" in foreign_key_targets
    assert "users.id" in foreign_key_targets

    check_constraint_names = {
        constraint.name
        for constraint in Message.__table__.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }

    assert "messages_sender_type_check" in check_constraint_names
    assert "messages_content_check" in check_constraint_names



def test_refund_model():
    assert "refunds" in Base.metadata.tables

    assert list(Refund.__table__.columns.keys()) == [
        "id",
        "order_id",
        "customer_id",
        "ticket_id",
        "amount",
        "reason",
        "status",
        "requested_by",
        "approved_by",
        "requested_at",
        "decided_at",
        "completed_at",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Refund.__table__.foreign_keys
    }

    assert "orders.id" in foreign_key_targets
    assert "customers.id" in foreign_key_targets
    assert "tickets.id" in foreign_key_targets
    assert "users.id" in foreign_key_targets


def test_refund_constraints_and_relationships():
    check_constraint_names = {
        constraint.name
        for constraint in Refund.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "refunds_amount_check" in check_constraint_names
    assert "refunds_status_check" in check_constraint_names

    assert Refund.order.property.uselist is False
    assert Refund.customer.property.uselist is False
    assert Refund.ticket.property.uselist is False
    assert Refund.requester.property.uselist is False
    assert Refund.approver.property.uselist is False


def test_document_model():
    assert "documents" in Base.metadata.tables

    assert list(Document.__table__.columns.keys()) == [
        "id",
        "title",
        "file_name",
        "document_type",
        "source",
        "uploaded_by",
        "created_at",
        "updated_at",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Document.__table__.foreign_keys
    }

    assert "users.id" in foreign_key_targets


def test_document_chunk_model():
    assert "document_chunks" in Base.metadata.tables

    assert list(DocumentChunk.__table__.columns.keys()) == [
        "id",
        "document_id",
        "chunk_index",
        "content",
        "embedding",
        "metadata",
        "created_at",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in DocumentChunk.__table__.foreign_keys
    }

    assert "documents.id" in foreign_key_targets

    document_fk = next(
        foreign_key
        for foreign_key in DocumentChunk.__table__.foreign_keys
        if foreign_key.target_fullname == "documents.id"
    )
    assert document_fk.ondelete == "CASCADE"

    assert DocumentChunk.document.property.uselist is False

    unique_constraints = {
        constraint.name
        for constraint in DocumentChunk.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert (
        "document_chunks_document_id_chunk_index_key"
        in unique_constraints
    )


def test_agent_run_model():
    assert "agent_runs" in Base.metadata.tables

    assert list(AgentRun.__table__.columns.keys()) == [
        "id",
        "conversation_id",
        "customer_id",
        "status",
        "model",
        "started_at",
        "completed_at",
        "error_message",
        "input_tokens",
        "output_tokens",
        "estimated_cost",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in AgentRun.__table__.foreign_keys
    }

    assert "conversations.id" in foreign_key_targets
    assert "customers.id" in foreign_key_targets


def test_agent_run_status_constraint():
    check_constraint_names = {
        constraint.name
        for constraint in AgentRun.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "agent_runs_status_check" in check_constraint_names


def test_agent_run_estimated_cost_precision():
    cost_column = AgentRun.__table__.c.estimated_cost

    assert cost_column.type.precision == 12
    assert cost_column.type.scale == 6
    assert cost_column.nullable is True


def test_tool_call_model():
    assert "tool_calls" in Base.metadata.tables

    assert list(ToolCall.__table__.columns.keys()) == [
        "id",
        "agent_run_id",
        "tool_name",
        "arguments",
        "result",
        "status",
        "error_message",
        "latency_ms",
        "created_at",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in ToolCall.__table__.foreign_keys
    }

    assert "agent_runs.id" in foreign_key_targets


def test_tool_call_column_types_and_nullability():
    columns = ToolCall.__table__.c

    assert isinstance(columns.arguments.type, JSONB)
    assert isinstance(columns.result.type, JSONB)

    assert columns.arguments.nullable is False
    assert columns.result.nullable is True
    assert columns.error_message.nullable is True
    assert columns.latency_ms.nullable is True

    assert columns.tool_name.type.length == 100
    assert columns.status.type.length == 30


def test_approval_model():
    assert "approvals" in Base.metadata.tables

    assert list(Approval.__table__.columns.keys()) == [
        "id",
        "agent_run_id",
        "tool_call_id",
        "ticket_id",
        "action",
        "status",
        "requested_at",
        "decided_at",
        "decided_by",
        "reason",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in Approval.__table__.foreign_keys
    }

    assert "agent_runs.id" in foreign_key_targets
    assert "tool_calls.id" in foreign_key_targets
    assert "tickets.id" in foreign_key_targets
    assert "users.id" in foreign_key_targets


def test_approval_constraints_and_nullability():
    check_constraint_names = {
        constraint.name
        for constraint in Approval.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "approvals_status_check" in check_constraint_names

    columns = Approval.__table__.c

    assert columns.agent_run_id.nullable is False
    assert columns.action.nullable is False
    assert columns.status.nullable is False
    assert columns.requested_at.nullable is False

    assert columns.tool_call_id.nullable is True
    assert columns.ticket_id.nullable is True
    assert columns.decided_at.nullable is True
    assert columns.decided_by.nullable is True
    assert columns.reason.nullable is True

    assert columns.action.type.length == 100
    assert columns.status.type.length == 30



def test_audit_log_model():
    assert "audit_logs" in Base.metadata.tables

    assert list(AuditLog.__table__.columns.keys()) == [
        "id",
        "actor_user_id",
        "actor_type",
        "action",
        "entity_type",
        "entity_id",
        "metadata",
        "created_at",
    ]

    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in AuditLog.__table__.foreign_keys
    }

    assert "users.id" in foreign_key_targets


def test_audit_log_column_types_and_defaults():
    columns = AuditLog.__table__.c

    assert columns.actor_user_id.nullable is True
    assert columns.actor_type.nullable is False
    assert columns.action.nullable is False
    assert columns.entity_type.nullable is False
    assert columns.entity_id.nullable is True
    assert columns.metadata.nullable is True

    assert columns.actor_type.type.length == 30
    assert columns.action.type.length == 100
    assert columns.entity_type.type.length == 100

    assert isinstance(columns.metadata.type, JSONB)

    assert columns.created_at.nullable is False
    assert columns.created_at.server_default is not None
