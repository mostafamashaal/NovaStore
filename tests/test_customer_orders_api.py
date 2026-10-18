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


def test_get_my_order_returns_order_with_items(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)

    item = SimpleNamespace(
        product_id=uuid4(),
        quantity=2,
        unit_price=Decimal("649.99"),
    )
    order = make_order(customer.id)
    order.items = [item]

    db.scalar.side_effect = [customer, order]

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(f"/customers/me/orders/{order.id}")
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(order.id)
    assert data["order_number"] == order.order_number
    assert data["total_amount"] == "1299.99"
    assert data["items"] == [
        {
            "product_id": str(item.product_id),
            "quantity": 2,
            "unit_price": "649.99",
        }
    ]
    assert "customer_id" not in data


def test_get_my_order_returns_404_for_another_customers_order(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)
    order = make_order(customer_id=uuid4())

    db.scalar.side_effect = [customer, order]

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(f"/customers/me/orders/{order.id}")
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_get_my_order_returns_404_when_order_does_not_exist(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)

    db.scalar.side_effect = [customer, None]

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(f"/customers/me/orders/{uuid4()}")
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_get_my_order_requires_authentication(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client

    response = client.get(f"/customers/me/orders/{uuid4()}")

    assert response.status_code == 401
    db.scalar.assert_not_called()


def test_get_my_order_status_history_returns_history(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)
    order = make_order(customer.id)

    history_entry = SimpleNamespace(
        id=uuid4(),
        order_id=order.id,
        old_status="processing",
        new_status="shipped",
        changed_at=datetime(2026, 10, 15, 12, 30, tzinfo=timezone.utc),
        changed_by_user_id=uuid4(),
        changed_by_type="system",
    )

    db.scalar.side_effect = [customer, order]
    db.scalars.return_value.all.return_value = [history_entry]

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(
            f"/customers/me/orders/{order.id}/history"
        )
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(history_entry.id),
            "old_status": "processing",
            "new_status": "shipped",
            "changed_at": "2026-10-15T12:30:00Z",
        }
    ]
    assert "changed_by_user_id" not in response.json()[0]
    assert "changed_by_type" not in response.json()[0]


def test_get_my_order_status_history_returns_empty_list(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)
    order = make_order(customer.id)

    db.scalar.side_effect = [customer, order]
    db.scalars.return_value.all.return_value = []

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(
            f"/customers/me/orders/{order.id}/history"
        )
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 200
    assert response.json() == []


def test_get_my_order_status_history_rejects_another_customers_order(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)
    order = make_order(customer_id=uuid4())

    db.scalar.side_effect = [customer, order]

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(
            f"/customers/me/orders/{order.id}/history"
        )
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    db.scalars.assert_not_called()


def test_get_my_order_status_history_returns_404_for_missing_order(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client
    user = make_user()
    customer = make_customer(user.id)

    db.scalar.side_effect = [customer, None]

    def override_get_current_user():
        return user

    original_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(
            f"/customers/me/orders/{uuid4()}/history"
        )
    finally:
        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    db.scalars.assert_not_called()


def test_get_my_order_status_history_requires_authentication(
    customer_orders_api_client,
):
    client, db = customer_orders_api_client

    response = client.get(
        f"/customers/me/orders/{uuid4()}/history"
    )

    assert response.status_code == 401
    db.scalar.assert_not_called()
    db.scalars.assert_not_called()
