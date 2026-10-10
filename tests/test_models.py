from src.models.base import Base
from sqlalchemy import CheckConstraint
from src.models.user import User
from src.models.customer import Customer

from src.models.inventory import Inventory
from src.models.product import Product

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
    