"""
Model de Pagamento - [RF04, RF10, RF11]
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.promissory_note import PromissoryNote


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    promissory_note_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("promissory_notes.id"),
        nullable=False,
        index=True,
    )

    amount_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)

    interest_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    fine_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relacionamento
    promissory_note: Mapped["PromissoryNote"] = relationship(
        "PromissoryNote",
        back_populates="payments",
    )

    @property
    def total_amount(self) -> Decimal:
        """Valor total do pagamento (principal + juros + multa)"""
        return self.amount_paid + self.interest_amount + self.fine_amount

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, promissory_note_id={self.promissory_note_id}, "
            f"amount={self.amount_paid})>"
        )

