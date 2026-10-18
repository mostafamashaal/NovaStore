from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user


def make_customer(user_id):
    return SimpleNamespace(
        id=uuid4(),
        user_id=user_id,
        first_name="Test",
        last_name="Customer",
        phone=None,
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
    )


def make_order(customer_id):
    return SimpleNamespace(
        id=uuid4(),
        customer_id=customer_id,
        order_number="NS-10452",
        status="delivered",
    )


def make_refund():
    return SimpleNamespace(
        id=uuid4(),
        order_id=uuid4(),
        customer_id=uuid4(),
        ticket_id=None,
        amount=Decimal("49.99"),
        reason="Product arrived damaged",
        status="completed",
        requested_by=None,
        approved_by=None,
        requested_at=datetime(2026, 10, 16, 9, 0, tzinfo=timezone.utc),
        decided_at=datetime(2026, 10, 16, 10, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc),
    )


def test_list_my_order_refunds_returns_public_fields():
    db = MagicMock()
    user = SimpleNamespace(
        id=uuid4(),
        email="customer@example.com",
        role="customer",
        is_active=True,
        password_hash="test-password-hash",
    )
    customer = make_customer(user.id)
    order = make_order(customer.id)
    refund = make_refund()
    refund.order_id = order.id
    refund.customer_id = customer.id

    db.scalar.side_effect = [customer, order]
    db.scalars.return_value.all.return_value = [refund]

    original_db_override = app.dependency_overrides.get(get_db)
    original_user_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/customers/me/orders/{order.id}/refunds"
            )
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override

        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 200
    assert response.json() == [
        {
            "amount": "49.99",
            "reason": "Product arrived damaged",
            "status": "completed",
            "requested_at": "2026-10-16T09:00:00Z",
            "decided_at": "2026-10-16T10:00:00Z",
            "completed_at": "2026-10-17T12:00:00Z",
        }
    ]

    assert "id" not in response.json()[0]
    assert "order_id" not in response.json()[0]
    assert "customer_id" not in response.json()[0]
    assert "approved_by" not in response.json()[0]


def test_list_my_order_refunds_returns_empty_list():
    db = MagicMock()
    user = SimpleNamespace(id=uuid4())
    customer = make_customer(user.id)
    order = make_order(customer.id)

    db.scalar.side_effect = [customer, order]
    db.scalars.return_value.all.return_value = []

    original_db_override = app.dependency_overrides.get(get_db)
    original_user_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/customers/me/orders/{order.id}/refunds"
            )
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override

        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 200
    assert response.json() == []


def test_list_my_order_refunds_returns_404_for_another_customers_order():
    db = MagicMock()
    user = SimpleNamespace(id=uuid4())
    customer = make_customer(user.id)
    order = make_order(customer_id=uuid4())

    db.scalar.side_effect = [customer, order]

    original_db_override = app.dependency_overrides.get(get_db)
    original_user_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/customers/me/orders/{order.id}/refunds"
            )
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override

        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    db.scalars.assert_not_called()


def test_list_my_order_refunds_returns_404_without_customer_profile():
    db = MagicMock()
    user = SimpleNamespace(id=uuid4())
    db.scalar.return_value = None

    original_db_override = app.dependency_overrides.get(get_db)
    original_user_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/customers/me/orders/{uuid4()}/refunds"
            )
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override

        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"
    db.scalars.assert_not_called()


def test_list_my_order_refunds_returns_404_for_missing_order():
    db = MagicMock()
    user = SimpleNamespace(id=uuid4())
    customer = make_customer(user.id)

    db.scalar.side_effect = [customer, None]

    original_db_override = app.dependency_overrides.get(get_db)
    original_user_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/customers/me/orders/{uuid4()}/refunds"
            )
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override

        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    db.scalars.assert_not_called()


def test_list_my_order_refunds_requires_authentication():
    db = MagicMock()
    user = SimpleNamespace(id=uuid4())

    original_db_override = app.dependency_overrides.get(get_db)
    original_user_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides.pop(get_current_user, None)

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/customers/me/orders/{uuid4()}/refunds"
            )
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override

        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override

    assert response.status_code == 401
    db.scalar.assert_not_called()
    db.scalars.assert_not_called()
