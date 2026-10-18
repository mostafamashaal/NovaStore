from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ShipmentResponse(BaseModel):
    """Public API representation of shipment tracking information."""

    model_config = ConfigDict(from_attributes=True)

    carrier: str
    tracking_number: str | None
    status: str
    estimated_delivery: date | None
    shipped_at: datetime | None
    delivered_at: datetime | None
