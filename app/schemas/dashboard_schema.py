from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class DashboardNextDueItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    promissory_note_id: int
    sale_id: int
    customer_id: int

    due_date: date

    original_amount: Decimal = Field(..., decimal_places=2)
    paid_amount: Decimal = Field(..., decimal_places=2)
    outstanding_balance: Decimal = Field(..., decimal_places=2)

    status: str


class DashboardOut(BaseModel):
    total_to_receive: Decimal = Field(..., decimal_places=2)
    total_overdue: Decimal = Field(..., decimal_places=2)
    received_last_30_days: Decimal = Field(..., decimal_places=2)

    next_due: List[DashboardNextDueItem]
