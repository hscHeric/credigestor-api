from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import TimestampSchema
from app.schemas.promissory_note_schema import PromissoryNoteOut


class SaleCreate(BaseModel):
    customer_id: int
    description: Optional[str] = None

    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    down_payment: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)

    installments_count: int = Field(..., gt=0)
    first_installment_date: date

    @field_validator("down_payment")
    @classmethod
    def validate_down_payment(cls, v: Decimal) -> Decimal:
        return v if v is not None else Decimal("0.00")


class SaleOut(TimestampSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    user_id: int

    description: Optional[str] = None
    total_amount: Decimal
    down_payment: Decimal

    installments_count: int
    first_installment_date: date


class SaleWithNotesOut(SaleOut):
    promissory_notes: List[PromissoryNoteOut]
