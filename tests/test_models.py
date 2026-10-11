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