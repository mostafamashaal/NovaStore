from uuid import UUID

from src.models.customer import Customer
from src.repositories.customer_repository import CustomerRepository


class CustomerService:
    """Business logic for customer operations."""

    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    def list_customers(self) -> list[Customer]:
        """Return the list of customers."""
        return self.customer_repository.list_customers()

    def get_customer_by_user_id(self, user_id: UUID) -> Customer | None:
        """Return the customer profile associated with a user."""
        return self.customer_repository.get_by_user_id(user_id)
