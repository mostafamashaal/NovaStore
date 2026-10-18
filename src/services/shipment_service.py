from uuid import UUID

from src.models.shipment import Shipment
from src.repositories.order_repository import OrderRepository
from src.repositories.shipment_repository import ShipmentRepository


class ShipmentService:
    """Business logic for customer shipment tracking."""

    def __init__(
        self,
        order_repository: OrderRepository,
        shipment_repository: ShipmentRepository,
    ) -> None:
        self.order_repository = order_repository
        self.shipment_repository = shipment_repository

    def list_shipments_for_customer(
        self,
        order_id: UUID,
        customer_id: UUID,
    ) -> list[Shipment] | None:
        """Return shipments only when the order belongs to the customer."""
        order = self.order_repository.get_by_id(order_id)

        if order is None or order.customer_id != customer_id:
            return None

        return self.shipment_repository.list_by_order(order_id)
