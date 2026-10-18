
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderStatusHistoryResponse(BaseModel):
    """Public API representation of an order status change."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    old_status: str | None
    new_status: str
    changed_at: datetime
