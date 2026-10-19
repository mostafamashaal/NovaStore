from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TicketResponse(BaseModel):
    """Public support ticket information returned to a customer."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_number: str
    category: str
    priority: str
    status: str
    subject: str
    description: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
