from uuid import UUID

from src.models.refund import Refund
from src.repositories.order_repository import OrderRepository
from src.repositories.refund_repository import RefundRepository


class RefundService:
    """Business logic for customer refund history."""

    def __init__(
        self,
        order_repository: OrderRepository,
        refund_repository: RefundRepository,
    ) -> None:
        self.order_repository = order_repository
        self.refund_repository = refund_repository

    def list_refunds_for_customer(
        self,
        order_id: UUID,
        customer_id: UUID,
    ) -> list[Refund] | None:
        """Return refunds only when the customer owns the order."""
        order = self.order_repository.get_by_id(order_id)

        if order is None or order.customer_id != customer_id:
            return None

        return self.refund_repository.list_by_order(order_id)
