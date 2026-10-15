from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.tokens import create_access_token


@pytest.fixture
def auth_me_client():
    """Provide a test client with a mocked database session."""
    db = MagicMock()

    original_override = app.dependency_overrides.get(get_db)

    def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client, db
    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_override


def make_user(*, is_active=True):
    """Create a lightweight user object for authentication tests."""
    return SimpleNamespace(
        id=uuid4(),
        email="test@example.com",
        role="customer",
        is_active=is_active,
        created_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
        password_hash="sensitive-hash-that-must-not-leak",
    )


def test_get_current_user_with_valid_token(auth_me_client):
    client, db = auth_me_client
    user = make_user()
    db.scalar.return_value = user

    token = create_access_token(user.id)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["role"] == user.role
    assert data["is_active"] is True
    assert "created_at" in data
    assert "password_hash" not in data


def test_get_current_user_without_token(auth_me_client):
    client, db = auth_me_client

    response = client.get("/auth/me")

    assert response.status_code == 401
    db.scalar.assert_not_called()


def test_get_current_user_with_invalid_token(auth_me_client):
    client, db = auth_me_client

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401
    db.scalar.assert_not_called()


def test_get_current_user_when_user_does_not_exist(auth_me_client):
    client, db = auth_me_client
    db.scalar.return_value = None

    token = create_access_token(uuid4())

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_get_current_user_when_user_is_inactive(auth_me_client):
    client, db = auth_me_client
    user = make_user(is_active=False)
    db.scalar.return_value = user

    token = create_access_token(user.id)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
