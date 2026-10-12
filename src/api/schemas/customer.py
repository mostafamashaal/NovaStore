from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    """Public API representation of a customer."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    phone: str | None
    created_at: datetime
