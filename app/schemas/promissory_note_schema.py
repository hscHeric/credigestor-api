from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict, Field

from app.schemas.base import TimestampSchema


class PromissoryNoteOut(TimestampSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int
    installment_number: int

    original_amount: Decimal = Field(..., decimal_places=2)
    paid_amount: Decimal = Field(..., decimal_places=2)

    due_date: date
    payment_date: Optional[date] = None

    status: str
    notes: Optional[str] = None
