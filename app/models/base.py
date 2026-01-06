"""
Base model com campos comuns
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin para adicionar timestamps automáticos"""

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
