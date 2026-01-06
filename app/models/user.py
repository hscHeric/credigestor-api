"""
Model de Usuário
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimestampMixin


class UserRole(str, enum.Enum):
    """Perfis de usuário do sistema"""

    ADMIN = "admin"
    SELLER = "seller"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    # Corrigir: passar o enum Python diretamente, não SQLEnum
    role = Column(String(20), nullable=False, default="seller")
    active = Column(Boolean, default=True, nullable=False)
    temporary_password = Column(Boolean, default=True, nullable=False)

    sales = relationship("Sale", back_populates="user")

    @property
    def role_enum(self) -> UserRole:
        """Retorna o role como enum"""
        return UserRole(self.role)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

