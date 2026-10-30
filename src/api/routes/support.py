from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.message import MessageCreateRequest, MessageResponse
from src.api.schemas.ticket import (
    TicketAssignmentRequest,
    TicketAssignmentResponse,
)
from src.db.dependencies import get_db
from src.models.user import User
from src.repositories.message_repository import MessageRepository
from src.repositories.ticket_repository import TicketRepository
from src.security.dependencies import get_current_user
from src.services.message_service import (
    MessageService,
    TicketAgentReplyForbiddenError,
    TicketReplyNotAllowedError,
)
from src.services.ticket_service import (
    InvalidSupportAgentError,
    TicketService,
)

router = APIRouter(prefix="/support", tags=["Support"])


@router.post(
    "/tickets/{ticket_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_support_ticket_message(
    ticket_id: UUID,
    payload: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Create a support-agent reply on an assigned ticket."""
    message_service = MessageService(
        message_repository=MessageRepository(db),
        ticket_repository=TicketRepository(db),
    )

    try:
        message = message_service.create_support_agent_reply(
            ticket_id=ticket_id,
            sender_user_id=current_user.id,
            sender_role=current_user.role,
            content=payload.content,
        )
    except TicketAgentReplyForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except TicketReplyNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return message


@router.patch(
    "/tickets/{ticket_id}/assignment",
    response_model=TicketAssignmentResponse,
)
def assign_support_ticket(
    ticket_id: UUID,
    payload: TicketAssignmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketAssignmentResponse:
    """Allow admins to assign, reassign, or unassign support tickets."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can assign support tickets.",
        )

    ticket_service = TicketService(TicketRepository(db))

    try:
        ticket = ticket_service.assign_ticket(
            ticket_id=ticket_id,
            agent_id=payload.agent_id,
        )
    except InvalidSupportAgentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket
