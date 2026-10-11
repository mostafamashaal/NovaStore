from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.product import Product


class ProductRepository:
    """Repository for database operations on products."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, product_id: UUID) -> Product | None:
        statement = select(Product).where(Product.id == product_id)
        return self.session.scalar(statement)

    def get_by_sku(self, sku: str) -> Product | None:
        statement = select(Product).where(Product.sku == sku)
        return self.session.scalar(statement)

    def list_active(self) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.name)
        )
        return list(self.session.scalars(statement).all())
