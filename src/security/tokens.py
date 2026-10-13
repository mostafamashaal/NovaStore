from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt

from src.config.settings import Settings


settings = Settings()


def create_access_token(user_id: UUID | str) -> str:
    """Create a signed JWT access token for a user."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify a JWT and return its claims."""
    return jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "iat", "exp"]},
    )
