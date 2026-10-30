from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated


TicketCategory = Literal[
    "refund",
    "complaint",
    "damaged_order",
    "technical",
    "shipping",
]

TicketPriority = Literal["low", "medium", "high", "urgent"]

TicketSubject = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]

TicketDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=5000),
]


class TicketCreateRequest(BaseModel):
    """Validated input for creating a customer support ticket."""
    model_config = ConfigDict(extra="forbid")

    category: TicketCategory
    priority: TicketPriority = "medium"
    subject: TicketSubject
    description: TicketDescription


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


class TicketStatusUpdateRequest(BaseModel):
    """Validated input for a customer-requested ticket status change."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["open", "closed"]


class TicketAssignmentRequest(BaseModel):
    """Input for assigning, reassigning, or unassigning a ticket."""

    model_config = ConfigDict(extra="forbid")

    agent_id: UUID | None


class TicketAssignmentResponse(BaseModel):
    """Staff-facing result of a ticket assignment operation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_number: str
    assigned_agent_id: UUID | None
    updated_at: datetime
