"""
Model de Promissória
"""

from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.sale import Sale
    from app.models.payment import Payment


class PromissoryNoteStatus(str, enum.Enum):
    """Status possíveis de uma promissória"""

    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIAL_PAYMENT = "partial_payment"


class PromissoryNote(Base, TimestampMixin):
    __tablename__ = "promissory_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales.id"), nullable=False, index=True
    )

    installment_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # Ex: 1, 2, 3...
    original_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Usar String em vez de Enum no DB
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=PromissoryNoteStatus.PENDING.value,
        index=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relacionamentos
    sale: Mapped["Sale"] = relationship("Sale", back_populates="promissory_notes")
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="promissory_note",
        cascade="all, delete-orphan",
    )

    @property
    def status_enum(self) -> PromissoryNoteStatus:
        """Retorna o status como enum"""
        return PromissoryNoteStatus(self.status)

    @property
    def outstanding_balance(self) -> Decimal:
        """Calcula o saldo devedor da promissória"""
        return self.original_amount - self.paid_amount

    @property
    def days_overdue(self) -> int:
        """Calcula quantos dias de atraso"""
        if self.status == PromissoryNoteStatus.PAID.value:
            return 0

        today = date.today()
        if today > self.due_date:
            return (today - self.due_date).days
        return 0

    @property
    def is_overdue(self) -> bool:
        """Verifica se a promissória está vencida"""
        return (
            date.today() > self.due_date
            and self.status != PromissoryNoteStatus.PAID.value
        )

    def __repr__(self) -> str:
        return (
            f"<PromissoryNote(id={self.id}, sale_id={self.sale_id}, "
            f"installment={self.installment_number}, status={self.status})>"
        )

