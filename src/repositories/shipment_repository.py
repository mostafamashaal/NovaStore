from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.shipment import Shipment


class ShipmentRepository:
    """Repository for database operations on shipments."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_order(self, order_id: UUID) -> list[Shipment]:
        """Return all shipments associated with an order."""
        statement = (
            select(Shipment)
            .where(Shipment.order_id == order_id)
            .order_by(Shipment.created_at.asc(), Shipment.id.asc())
        )

        return list(self.session.scalars(statement).all())
