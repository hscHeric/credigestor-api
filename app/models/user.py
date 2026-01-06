"""
Model de Usuário
"""

from __future__ import annotations

import enum
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.sale import Sale


class UserRole(str, enum.Enum):
    """Perfis de usuário do sistema"""

    ADMIN = "admin"
    SELLER = "seller"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False, index=True
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Mantém como String para evitar complicações de enum no DB (simples e compatível)
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.SELLER.value,
    )

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    temporary_password: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="user")

    @property
    def role_enum(self) -> UserRole:
        """Retorna o role como enum"""
        return UserRole(self.role)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
