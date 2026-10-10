from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.product import Product



class Inventory(Base):
    """ORM model representing the existing inventory table."""

    __tablename__ = "inventory"

    __table_args__ = (
        CheckConstraint(
            "available_quantity >= 0",
            name="inventory_available_quantity_check",
        ),
        CheckConstraint(
            "reserved_quantity >= 0",
            name="inventory_reserved_quantity_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    product_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        unique=True,
    )

    available_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reserved_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="inventory",
    )