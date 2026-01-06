"""
Model de Pagamento - [RF04, RF10, RF11]
"""

from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    promissory_note_id = Column(
        Integer, ForeignKey("promissory_notes.id"), nullable=False, index=True
    )

    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)

    interest_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    fine_amount = Column(Numeric(10, 2), default=0.00, nullable=False)

    notes = Column(Text, nullable=True)

    # Relacionamento
    promissory_note = relationship("PromissoryNote", back_populates="payments")

    @property
    def total_amount(self) -> float:
        """Valor total do pagamento (principal + juros + multa)"""
        return (
            float(self.amount_paid)
            + float(self.interest_amount)
            + float(self.fine_amount)
        )

    def __repr__(self):
        return f"<Payment(id={self.id}, promissory_note_id={self.promissory_note_id}, amount={self.amount_paid})>"
