"""
Model de Venda
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.user import User
    from app.models.promissory_note import PromissoryNote


class Sale(Base, TimestampMixin):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    down_payment: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    installments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    first_installment_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relacionamentos
    customer: Mapped["Customer"] = relationship("Customer", back_populates="sales")
    user: Mapped["User"] = relationship("User", back_populates="sales")
    promissory_notes: Mapped[List["PromissoryNote"]] = relationship(
        "PromissoryNote",
        back_populates="sale",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Sale(id={self.id}, customer_id={self.customer_id}, "
            f"total_amount={self.total_amount})>"
        )

