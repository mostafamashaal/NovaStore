from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user


@pytest.fixture
def customer_orders_api_client():
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


def make_order(customer_id, order_number="NS-10452"):
    return SimpleNamespace(
        id=uuid4(),
        customer_id=customer_id,
        order_number=order_number,
        status="processing",
        total_amount=Decimal("1299.99"),
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
    )


def test_list_my_orders_returns_only_public_order_fields(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)
    order = make_order(customer.id)

    db.scalar.return_value = customer
    db.scalars.return_value.all.return_value = [order]

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get("/customers/me/orders")
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(order.id),
            "order_number": "NS-10452",
            "status": "processing",
            "total_amount": "1299.99",
            "created_at": "2026-10-15T00:00:00Z",
        }
    ]

    statement = db.scalars.call_args.args[0]
    assert customer.id in statement.compile().params.values()


def test_list_my_orders_returns_empty_list_when_customer_has_no_orders(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)

    db.scalar.return_value = customer
    db.scalars.return_value.all.return_value = []

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get("/customers/me/orders")
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 200
    assert response.json() == []


def test_list_my_orders_returns_404_when_customer_profile_is_missing(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()

    db.scalar.return_value = None

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get("/customers/me/orders")
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"
    db.scalars.assert_not_called()


def test_list_my_orders_requires_authentication(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client

    response = client.get("/customers/me/orders")

    assert response.status_code == 401
    db.scalar.assert_not_called()
    db.scalars.assert_not_called()
