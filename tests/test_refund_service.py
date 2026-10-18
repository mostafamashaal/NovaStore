from unittest.mock import MagicMock
from uuid import uuid4

from src.models.order import Order
from src.models.refund import Refund
from src.repositories.order_repository import OrderRepository
from src.repositories.refund_repository import RefundRepository
from src.services.refund_service import RefundService


def test_list_refunds_returns_refunds_when_customer_owns_order():
    order_repository = MagicMock(spec=OrderRepository)
    refund_repository = MagicMock(spec=RefundRepository)

    order_id = uuid4()
    customer_id = uuid4()

    order = MagicMock(spec=Order)
    order.customer_id = customer_id

    refunds = [MagicMock(spec=Refund)]
    order_repository.get_by_id.return_value = order
    refund_repository.list_by_order.return_value = refunds

    service = RefundService(order_repository, refund_repository)

    result = service.list_refunds_for_customer(order_id, customer_id)

    assert result == refunds
    order_repository.get_by_id.assert_called_once_with(order_id)
    refund_repository.list_by_order.assert_called_once_with(order_id)


def test_list_refunds_returns_none_when_order_does_not_exist():
    order_repository = MagicMock(spec=OrderRepository)
    refund_repository = MagicMock(spec=RefundRepository)

    order_id = uuid4()
    customer_id = uuid4()
    order_repository.get_by_id.return_value = None

    service = RefundService(order_repository, refund_repository)

    result = service.list_refunds_for_customer(order_id, customer_id)

    assert result is None
    refund_repository.list_by_order.assert_not_called()


def test_list_refunds_returns_none_when_customer_does_not_own_order():
    order_repository = MagicMock(spec=OrderRepository)
    refund_repository = MagicMock(spec=RefundRepository)

    order_id = uuid4()
    owner_customer_id = uuid4()
    other_customer_id = uuid4()

    order = MagicMock(spec=Order)
    order.customer_id = owner_customer_id
    order_repository.get_by_id.return_value = order

    service = RefundService(order_repository, refund_repository)

    result = service.list_refunds_for_customer(
        order_id,
        other_customer_id,
    )

    assert result is None
    refund_repository.list_by_order.assert_not_called()
