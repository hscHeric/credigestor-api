"""
Model de Venda - [RF03]
"""

from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Sale(Base, TimestampMixin):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    description = Column(Text, nullable=True)  # Descrição dos produtos/serviços
    total_amount = Column(Numeric(10, 2), nullable=False)
    down_payment = Column(Numeric(10, 2), default=0.00, nullable=False)
    installments_count = Column(Integer, nullable=False)
    first_installment_date = Column(Date, nullable=False)

    # Relacionamentos
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    promissory_notes = relationship(
        "PromissoryNote", back_populates="sale", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Sale(id={self.id}, customer_id={self.customer_id}, total_amount={self.total_amount})>"
