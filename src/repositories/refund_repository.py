from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.refund import Refund


class RefundRepository:
    """Repository for database operations on refunds."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_order(self, order_id: UUID) -> list[Refund]:
        """Return refunds for an order in chronological order."""
        statement = (
            select(Refund)
            .where(Refund.order_id == order_id)
            .order_by(
                Refund.requested_at.asc(),
                Refund.id.asc(),
            )
        )
        return list(self.session.scalars(statement).all())
