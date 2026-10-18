from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RefundResponse(BaseModel):
    """Public refund information returned to a customer."""

    model_config = ConfigDict(from_attributes=True)

    amount: Decimal
    reason: str
    status: str
    requested_at: datetime
    decided_at: datetime | None
    completed_at: datetime | None
