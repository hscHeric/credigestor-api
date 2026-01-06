"""
Model de Configuração do Sistema - [RF15]
"""

from sqlalchemy import Column, Integer, String, Numeric, Text
from app.database import Base
from app.models.base import TimestampMixin


class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)

    company_name = Column(String(200), nullable=False, default="Minha Empresa")
    logo_url = Column(Text, nullable=True)

    monthly_interest_rate = Column(Numeric(5, 2), default=1.00, nullable=False)
    fine_rate = Column(Numeric(5, 2), default=2.00, nullable=False)

    days_before_due_alert = Column(Integer, default=5, nullable=False)

    def __repr__(self):
        return f"<SystemConfig(id={self.id}, company={self.company_name})>"
