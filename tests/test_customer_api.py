from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.dependencies import get_current_user
from src.security.tokens import create_access_token


@pytest.fixture
def customer_api_client():
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
        phone="+201000000000",
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
    )


def test_get_my_customer_profile(customer_api_client):
    client, db = customer_api_client
    user = make_user()
    customer = make_customer(user.id)

    db.scalar.return_value = customer

    def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        token = create_access_token(user.id)

        response = client.get(
            "/customers/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(customer.id)
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Customer"
    assert data["phone"] == "+201000000000"
    assert "user_id" not in data
    assert "password_hash" not in data


def test_get_my_customer_profile_not_found(customer_api_client):
    client, db = customer_api_client
    user = make_user()

    db.scalar.return_value = None

    def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        token = create_access_token(user.id)

        response = client.get(
            "/customers/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer profile not found"


def test_get_my_customer_profile_requires_authentication(
    customer_api_client,
):
    client, db = customer_api_client

    response = client.get("/customers/me")

    assert response.status_code == 401
    db.scalar.assert_not_called()
