"""
Model de Promissória - [RF03, RF04, RF06, RF09, RF10]
"""

from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, String, Text
from sqlalchemy.orm import relationship
import enum
from datetime import date
from app.database import Base
from app.models.base import TimestampMixin


class PromissoryNoteStatus(str, enum.Enum):
    """Status possíveis de uma promissória"""

    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIAL_PAYMENT = "partial_payment"


class PromissoryNote(Base, TimestampMixin):
    __tablename__ = "promissory_notes"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)

    installment_number = Column(Integer, nullable=False)  # Ex: 1, 2, 3...
    original_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    payment_date = Column(Date, nullable=True)

    # Usar String em vez de Enum
    status = Column(String(20), nullable=False, default="pending", index=True)

    notes = Column(Text, nullable=True)

    # Relacionamentos
    sale = relationship("Sale", back_populates="promissory_notes")
    payments = relationship(
        "Payment", back_populates="promissory_note", cascade="all, delete-orphan"
    )

    @property
    def status_enum(self) -> PromissoryNoteStatus:
        """Retorna o status como enum"""
        return PromissoryNoteStatus(self.status)

    @property
    def outstanding_balance(self) -> float:
        """Calcula o saldo devedor da promissória"""
        return float(self.original_amount) - float(self.paid_amount)

    @property
    def days_overdue(self) -> int:
        """Calcula quantos dias de atraso"""
        if self.status == "paid":
            return 0

        today = date.today()
        if today > self.due_date:
            return (today - self.due_date).days
        return 0

    @property
    def is_overdue(self) -> bool:
        """Verifica se a promissória está vencida"""
        return date.today() > self.due_date and self.status != "paid"

    def __repr__(self):
        return f"<PromissoryNote(id={self.id}, sale_id={self.sale_id}, installment={self.installment_number}, status={self.status})>"
