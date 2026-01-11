from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import TimestampSchema


class SystemConfigOut(TimestampSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    logo_url: Optional[str] = None

    monthly_interest_rate: Decimal = Field(..., decimal_places=2)
    fine_rate: Decimal = Field(..., decimal_places=2)

    days_before_due_alert: int


class SystemConfigUpdate(BaseModel):
    company_name: Optional[str] = None
    logo_url: Optional[str] = None

    monthly_interest_rate: Optional[Decimal] = Field(
        default=None, ge=0, decimal_places=2
    )
    fine_rate: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)

    days_before_due_alert: Optional[int] = Field(default=None, ge=0)
