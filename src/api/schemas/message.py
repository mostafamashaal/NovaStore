from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated


MessageContent = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=5000,
    ),
]


class MessageCreateRequest(BaseModel):
    """Validated input for a customer support ticket reply."""

    model_config = ConfigDict(extra="forbid")

    content: MessageContent


class MessageResponse(BaseModel):
    """Public message information returned to a customer."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sender_type: Literal["customer", "support_agent", "ai", "system", "tool"]
    content: str
    created_at: datetime
