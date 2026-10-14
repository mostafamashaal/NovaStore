from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.dependencies import get_db
from src.security.passwords import hash_password
from src.security.tokens import decode_access_token



@pytest.fixture
def auth_client():
    """Provide an API client with a mocked database session."""
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



def make_user(*, password="CorrectPassword123!", is_active=True):
    """Create a lightweight user object for authentication tests."""
    return SimpleNamespace(
        id=uuid4(),
        email="test@example.com",
        password_hash=hash_password(password),
        is_active=is_active,
    )


def test_login_success_returns_access_token(auth_client):
    client, db = auth_client
    user = make_user()
    db.scalar.return_value = user

    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "CorrectPassword123!",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    claims = decode_access_token(body["access_token"])
    assert claims["sub"] == str(user.id)


def test_login_rejects_wrong_password(auth_client):
    client, db = auth_client
    user = make_user()
    db.scalar.return_value = user

    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_rejects_unknown_email(auth_client):
    client, db = auth_client
    db.scalar.return_value = None

    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "CorrectPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_rejects_inactive_user(auth_client):
    client, db = auth_client
    user = make_user(is_active=False)
    db.scalar.return_value = user

    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "CorrectPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_rejects_invalid_email(auth_client):
    client, db = auth_client

    response = client.post(
        "/auth/login",
        json={
            "email": "not-an-email",
            "password": "CorrectPassword123!",
        },
    )

    assert response.status_code == 422
    db.scalar.assert_not_called()


def test_login_rejects_missing_password(auth_client):
    client, db = auth_client

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 422
    db.scalar.assert_not_called()


def test_login_rejects_empty_password(auth_client):
    client, db = auth_client

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "",
        },
    )

    assert response.status_code == 422
    db.scalar.assert_not_called()
