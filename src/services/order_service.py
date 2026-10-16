from uuid import UUID

from src.models.order import Order
from src.repositories.order_repository import OrderRepository


class OrderService:
    """Business logic for customer order operations."""

    def __init__(self, order_repository: OrderRepository) -> None:
        self.order_repository = order_repository

    def get_order_for_customer(
        self,
        order_id: UUID,
        customer_id: UUID,
    ) -> Order | None:
        """Return an order with its items only if it belongs to the customer."""
        order = self.order_repository.get_with_items(order_id)

        if order is None or order.customer_id != customer_id:
            return None

        return order

    def list_orders_for_customer(
        self,
        customer_id: UUID,
    ) -> list[Order]:
        """Return all orders belonging to a customer."""
        return self.order_repository.list_by_customer(customer_id)
