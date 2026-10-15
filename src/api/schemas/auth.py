from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    field_validator,
)


class LoginRequest(BaseModel):
    """Validated input for the login endpoint."""

    email: EmailStr
    password: SecretStr

    @field_validator("email", mode="before")
    @classmethod
    def strip_email_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("password")
    @classmethod
    def password_must_not_be_empty(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value():
            raise ValueError("Password must not be empty.")
        return value


class TokenResponse(BaseModel):
    """Access token returned after successful authentication."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class CurrentUserResponse(BaseModel):
    """Safe public representation of the authenticated user."""

    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
