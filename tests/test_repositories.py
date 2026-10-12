from unittest.mock import MagicMock

from src.models.customer import Customer
from src.models.order import Order
from src.models.product import Product
from src.repositories.customer_repository import CustomerRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository


def test_product_repository_get_by_id():
    session = MagicMock()
    product = MagicMock(spec=Product)
    session.scalar.return_value = product

    repository = ProductRepository(session)
    result = repository.get_by_id(product.id)

    assert result is product
    session.scalar.assert_called_once()


def test_product_repository_get_by_sku():
    session = MagicMock()
    product = MagicMock(spec=Product)
    session.scalar.return_value = product

    repository = ProductRepository(session)
    result = repository.get_by_sku(product.sku)

    assert result is product
    session.scalar.assert_called_once()


def test_product_repository_list_active():
    session = MagicMock()
    products = [MagicMock(spec=Product), MagicMock(spec=Product)]
    session.scalars.return_value.all.return_value = products

    repository = ProductRepository(session)
    result = repository.list_active()

    assert result == products
    session.scalars.assert_called_once()


def test_order_repository_get_by_id():
    session = MagicMock()
    order = MagicMock(spec=Order)
    session.scalar.return_value = order

    repository = OrderRepository(session)
    result = repository.get_by_id(order.id)

    assert result is order
    session.scalar.assert_called_once()


def test_order_repository_get_by_order_number():
    session = MagicMock()
    order = MagicMock(spec=Order)
    session.scalar.return_value = order

    repository = OrderRepository(session)
    result = repository.get_by_order_number(order.order_number)

    assert result is order
    session.scalar.assert_called_once()


def test_order_repository_list_by_customer():
    session = MagicMock()
    customer_id = MagicMock()
    orders = [MagicMock(spec=Order), MagicMock(spec=Order)]
    session.scalars.return_value.all.return_value = orders

    repository = OrderRepository(session)
    result = repository.list_by_customer(customer_id)

    assert result == orders
    session.scalars.assert_called_once()


def test_order_repository_get_with_items():
    session = MagicMock()
    order = MagicMock(spec=Order)
    session.scalar.return_value = order

    repository = OrderRepository(session)
    result = repository.get_with_items(order.id)

    assert result is order
    session.scalar.assert_called_once()


def test_customer_repository_get_by_id():
    session = MagicMock()
    customer = MagicMock(spec=Customer)
    session.scalar.return_value = customer

    repository = CustomerRepository(session)
    result = repository.get_by_id(customer.id)

    assert result is customer
    session.scalar.assert_called_once()


def test_customer_repository_get_by_user_id():
    session = MagicMock()
    customer = MagicMock(spec=Customer)
    session.scalar.return_value = customer

    repository = CustomerRepository(session)
    result = repository.get_by_user_id(customer.user_id)

    assert result is customer
    session.scalar.assert_called_once()


def test_customer_repository_list_customers():
    session = MagicMock()
    customers = [
        MagicMock(spec=Customer),
        MagicMock(spec=Customer),
    ]
    session.scalars.return_value.all.return_value = customers

    repository = CustomerRepository(session)
    result = repository.list_customers()

    assert result == customers
    session.scalars.assert_called_once()
