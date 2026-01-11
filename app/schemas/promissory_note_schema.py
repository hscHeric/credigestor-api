from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import TimestampSchema


class PromissoryNoteListItem(TimestampSchema):
    """
    Item de listagem de promissórias para RF06.
    Inclui dados do cliente (via join) para facilitar telas.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int

    customer_id: int
    customer_name: str

    installment_number: int
    due_date: date

    original_amount: Decimal = Field(..., decimal_places=2)
    paid_amount: Decimal = Field(..., decimal_places=2)
    outstanding_balance: Decimal = Field(..., decimal_places=2)

    status: str


class PromissoryNoteListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[PromissoryNoteListItem]
    total: int
    message: Optional[str] = None


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
