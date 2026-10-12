from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.customer import Customer


class CustomerRepository:
    """Repository for database operations on customers."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, customer_id: UUID) -> Customer | None:
        statement = select(Customer).where(Customer.id == customer_id)
        return self.session.scalar(statement)

    def get_by_user_id(self, user_id: UUID) -> Customer | None:
        statement = select(Customer).where(Customer.user_id == user_id)
        return self.session.scalar(statement)

    def list_customers(self) -> list[Customer]:
        statement = select(Customer).order_by(
            Customer.last_name,
            Customer.first_name,
        )
        return list(self.session.scalars(statement).all())
