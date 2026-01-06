"""
Model de Cliente - [RF02, RF07]
"""

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True)  # XXX.XXX.XXX-XX
    phone = Column(String(20), nullable=False)
    email = Column(String(200), nullable=True)
    address = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    sales = relationship("Sale", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.full_name}, cpf={self.cpf})>"
