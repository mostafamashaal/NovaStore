from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user


@pytest.fixture
def shipment_api_client():
    """Provide a test client with mocked database and authentication."""
    db = MagicMock()
    user = SimpleNamespace(
        id=uuid4(),
        email="customer@example.com",
        role="customer",
        is_active=True,
        password_hash="test-password-hash",
    )

    original_db_override = app.dependency_overrides.get(get_db)
    original_user_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with TestClient(app) as client:
            yield client, db, user
    finally:
        if original_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_db_override

        if original_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = original_user_override


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
        status="shipped",
    )


def make_shipment(order_id):
    return SimpleNamespace(
        id=uuid4(),
        order_id=order_id,
        carrier="DHL",
        tracking_number="DHL123456789",
        status="in_transit",
        estimated_delivery=date(2026, 10, 22),
        shipped_at=datetime(2026, 10, 17, 10, 30, tzinfo=timezone.utc),
        delivered_at=None,
        created_at=datetime(2026, 10, 17, 10, 30, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 17, 10, 30, tzinfo=timezone.utc),
    )


def test_list_my_order_shipments_returns_public_tracking_fields(
    shipment_api_client,
):
    client, db, user = shipment_api_client
    customer = make_customer(user.id)
    order = make_order(customer.id)
    shipment = make_shipment(order.id)

    db.scalar.side_effect = [customer, order]
    db.scalars.return_value.all.return_value = [shipment]

    response = client.get(
        f"/customers/me/orders/{order.id}/shipments"
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "carrier": "DHL",
            "tracking_number": "DHL123456789",
            "status": "in_transit",
            "estimated_delivery": "2026-10-22",
            "shipped_at": "2026-10-17T10:30:00Z",
            "delivered_at": None,
        }
    ]

    assert "order_id" not in response.json()[0]
    assert "id" not in response.json()[0]
    db.scalars.assert_called_once()


def test_list_my_order_shipments_returns_empty_list(
    shipment_api_client,
):
    client, db, user = shipment_api_client
    customer = make_customer(user.id)
    order = make_order(customer.id)

    db.scalar.side_effect = [customer, order]
    db.scalars.return_value.all.return_value = []

    response = client.get(
        f"/customers/me/orders/{order.id}/shipments"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_my_order_shipments_rejects_another_customers_order(
    shipment_api_client,
):
    client, db, user = shipment_api_client
    customer = make_customer(user.id)
    order = make_order(customer_id=uuid4())

    db.scalar.side_effect = [customer, order]

    response = client.get(
        f"/customers/me/orders/{order.id}/shipments"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    db.scalars.assert_not_called()


def test_list_my_order_shipments_returns_404_for_missing_order(
    shipment_api_client,
):
    client, db, user = shipment_api_client
    customer = make_customer(user.id)

    db.scalar.side_effect = [customer, None]

    response = client.get(
        f"/customers/me/orders/{uuid4()}/shipments"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    db.scalars.assert_not_called()


def test_list_my_order_shipments_returns_404_without_customer_profile(
    shipment_api_client,
):
    client, db, user = shipment_api_client
    db.scalar.return_value = None

    response = client.get(
        f"/customers/me/orders/{uuid4()}/shipments"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"
    db.scalars.assert_not_called()


def test_list_my_order_shipments_requires_authentication(
    shipment_api_client,
):
    client, db, user = shipment_api_client

    app.dependency_overrides.pop(get_current_user, None)

    try:
        response = client.get(
            f"/customers/me/orders/{uuid4()}/shipments"
        )
    finally:
        app.dependency_overrides[get_current_user] = lambda: user

    assert response.status_code == 401
    db.scalar.assert_not_called()
    db.scalars.assert_not_called()
