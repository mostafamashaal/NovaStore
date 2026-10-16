from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderSummaryResponse(BaseModel):
    """Public API representation of an order summary."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    status: str
    total_amount: Decimal
    created_at: datetime
