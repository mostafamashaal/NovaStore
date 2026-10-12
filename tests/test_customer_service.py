from unittest.mock import MagicMock

from src.services.customer_service import CustomerService


def test_list_customers_returns_repository_results():
    customer_repository = MagicMock()
    expected_customers = [MagicMock(), MagicMock()]

    customer_repository.list_customers.return_value = expected_customers

    customer_service = CustomerService(customer_repository)

    result = customer_service.list_customers()

    assert result == expected_customers
    customer_repository.list_customers.assert_called_once_with()
