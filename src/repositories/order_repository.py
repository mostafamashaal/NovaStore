from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.order import Order


class OrderRepository:
    """Repository for database operations on orders."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, order_id: UUID) -> Order | None:
        statement = select(Order).where(Order.id == order_id)
        return self.session.scalar(statement)

    def get_by_order_number(self, order_number: str) -> Order | None:
        statement = select(Order).where(
            Order.order_number == order_number
        )
        return self.session.scalar(statement)

    def list_by_customer(self, customer_id: UUID) -> list[Order]:
        statement = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
        )
        return list(self.session.scalars(statement).all())

    def get_with_items(self, order_id: UUID) -> Order | None:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return self.session.scalar(statement)
