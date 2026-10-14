from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.security.dependencies import get_current_user
from src.security.tokens import create_access_token


def make_credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def test_get_current_user_returns_active_user() -> None:
    user_id = uuid4()
    user = SimpleNamespace(id=user_id, is_active=True)

    db = MagicMock()
    db.scalar.return_value = user

    result = get_current_user(
        credentials=make_credentials(create_access_token(user_id)),
        db=db,
    )

    assert result is user
    db.scalar.assert_called_once()


def test_get_current_user_rejects_missing_credentials() -> None:
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=None, db=db)

    assert exc_info.value.status_code == 401
    db.scalar.assert_not_called()


def test_get_current_user_rejects_invalid_token() -> None:
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials=make_credentials("invalid-token"),
            db=db,
        )

    assert exc_info.value.status_code == 401
    db.scalar.assert_not_called()


def test_get_current_user_rejects_unknown_user() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials=make_credentials(create_access_token(uuid4())),
            db=db,
        )

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_inactive_user() -> None:
    user_id = uuid4()
    user = SimpleNamespace(id=user_id, is_active=False)

    db = MagicMock()
    db.scalar.return_value = user

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials=make_credentials(create_access_token(user_id)),
            db=db,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"
