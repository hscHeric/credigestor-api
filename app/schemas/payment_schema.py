from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import TimestampSchema


class PaymentCreate(BaseModel):
    amount_paid: Decimal = Field(..., gt=0, decimal_places=2)
    payment_date: date

    interest_amount: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    fine_amount: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)

    notes: Optional[str] = None


class PaymentOut(TimestampSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    promissory_note_id: int

    amount_paid: Decimal
    payment_date: date

    interest_amount: Decimal
    fine_amount: Decimal

    notes: Optional[str] = None
