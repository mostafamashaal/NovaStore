from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from src.config.settings import Settings
from src.security.tokens import create_access_token, decode_access_token


def test_create_and_decode_access_token() -> None:
    user_id = uuid4()

    token = create_access_token(user_id)
    claims = decode_access_token(token)

    assert claims["sub"] == str(user_id)
    assert "iat" in claims
    assert "exp" in claims


def test_decode_access_token_rejects_expired_token() -> None:
    settings = Settings()
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_decode_access_token_rejects_invalid_signature() -> None:
    settings = Settings()

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "deliberately-wrong-test-secret-32-bytes",
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(token)


def test_decode_access_token_rejects_malformed_token() -> None:
    with pytest.raises(jwt.DecodeError):
        decode_access_token("this-is-not-a-valid-jwt")


def test_decode_access_token_requires_exp_claim() -> None:
    settings = Settings()
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": now,
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(jwt.MissingRequiredClaimError):
        decode_access_token(token)
