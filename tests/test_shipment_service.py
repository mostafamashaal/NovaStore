from unittest.mock import MagicMock
from uuid import uuid4

from src.models.order import Order
from src.models.shipment import Shipment
from src.repositories.order_repository import OrderRepository
from src.repositories.shipment_repository import ShipmentRepository
from src.services.shipment_service import ShipmentService


def test_list_shipments_returns_shipments_when_customer_owns_order():
    order_repository = MagicMock(spec=OrderRepository)
    shipment_repository = MagicMock(spec=ShipmentRepository)

    order_id = uuid4()
    customer_id = uuid4()

    order = MagicMock(spec=Order)
    order.customer_id = customer_id

    shipments = [MagicMock(spec=Shipment)]
    order_repository.get_by_id.return_value = order
    shipment_repository.list_by_order.return_value = shipments

    service = ShipmentService(order_repository, shipment_repository)

    result = service.list_shipments_for_customer(order_id, customer_id)

    assert result == shipments
    order_repository.get_by_id.assert_called_once_with(order_id)
    shipment_repository.list_by_order.assert_called_once_with(order_id)


def test_list_shipments_returns_none_when_order_does_not_exist():
    order_repository = MagicMock(spec=OrderRepository)
    shipment_repository = MagicMock(spec=ShipmentRepository)

    order_id = uuid4()
    customer_id = uuid4()
    order_repository.get_by_id.return_value = None

    service = ShipmentService(order_repository, shipment_repository)

    result = service.list_shipments_for_customer(order_id, customer_id)

    assert result is None
    shipment_repository.list_by_order.assert_not_called()


def test_list_shipments_returns_none_when_customer_does_not_own_order():
    order_repository = MagicMock(spec=OrderRepository)
    shipment_repository = MagicMock(spec=ShipmentRepository)

    order_id = uuid4()
    owner_customer_id = uuid4()
    other_customer_id = uuid4()

    order = MagicMock(spec=Order)
    order.customer_id = owner_customer_id
    order_repository.get_by_id.return_value = order

    service = ShipmentService(order_repository, shipment_repository)

    result = service.list_shipments_for_customer(
        order_id,
        other_customer_id,
    )

    assert result is None
    shipment_repository.list_by_order.assert_not_called()
