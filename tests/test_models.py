from src.models.base import Base
from src.models.user import User
from src.models.customer import Customer


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