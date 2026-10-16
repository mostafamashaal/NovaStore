from unittest.mock import MagicMock
from uuid import uuid4

from src.services.customer_service import CustomerService


def test_list_customers_returns_repository_results():
    customer_repository = MagicMock()
    expected_customers = [MagicMock(), MagicMock()]

    customer_repository.list_customers.return_value = expected_customers

    customer_service = CustomerService(customer_repository)

    result = customer_service.list_customers()

    assert result == expected_customers
    customer_repository.list_customers.assert_called_once_with()


def test_get_customer_by_user_id_returns_repository_result():
    customer_repository = MagicMock()
    user_id = uuid4()
    expected_customer = MagicMock()

    customer_repository.get_by_user_id.return_value = expected_customer

    customer_service = CustomerService(customer_repository)

    result = customer_service.get_customer_by_user_id(user_id)

    assert result == expected_customer
    customer_repository.get_by_user_id.assert_called_once_with(user_id)
