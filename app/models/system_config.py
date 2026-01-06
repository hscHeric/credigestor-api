"""
Model de Configuração do Sistema - [RF15]
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="Minha Empresa",
    )
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    monthly_interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("1.00"),
    )
    fine_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("2.00"),
    )

    days_before_due_alert: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    def __repr__(self) -> str:
        return f"<SystemConfig(id={self.id}, company={self.company_name})>"
