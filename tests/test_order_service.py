from unittest.mock import MagicMock
from uuid import uuid4

from src.models.order import Order
from src.repositories.order_repository import OrderRepository
from src.services.order_service import OrderService


def test_get_order_for_customer_returns_order_when_customer_owns_it():
    repository = MagicMock(spec=OrderRepository)
    order = MagicMock(spec=Order)

    order_id = uuid4()
    customer_id = uuid4()
    order.customer_id = customer_id

    repository.get_with_items.return_value = order
    service = OrderService(repository)

    result = service.get_order_for_customer(order_id, customer_id)

    assert result is order
    repository.get_with_items.assert_called_once_with(order_id)


def test_get_order_for_customer_returns_none_when_order_not_found():
    repository = MagicMock(spec=OrderRepository)
    order_id = uuid4()
    customer_id = uuid4()

    repository.get_with_items.return_value = None
    service = OrderService(repository)

    result = service.get_order_for_customer(order_id, customer_id)

    assert result is None
    repository.get_with_items.assert_called_once_with(order_id)


def test_get_order_for_customer_returns_none_when_customer_does_not_own_order():
    repository = MagicMock(spec=OrderRepository)
    order = MagicMock(spec=Order)

    order_id = uuid4()
    owner_customer_id = uuid4()
    other_customer_id = uuid4()
    order.customer_id = owner_customer_id

    repository.get_with_items.return_value = order
    service = OrderService(repository)

    result = service.get_order_for_customer(
        order_id,
        other_customer_id,
    )

    assert result is None
    repository.get_with_items.assert_called_once_with(order_id)
