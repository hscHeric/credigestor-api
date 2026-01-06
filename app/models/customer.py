"""
Model de Cliente
"""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.sale import Sale


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # XXX.XXX.XXX-XX
    cpf: Mapped[str] = mapped_column(
        String(14), unique=True, nullable=False, index=True
    )

    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relacionamentos
    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name={self.full_name}, cpf={self.cpf})>"
