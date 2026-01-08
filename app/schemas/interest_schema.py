from __future__ import annotations

from decimal import Decimal
from pydantic import BaseModel, Field


class InterestFineBreakdown(BaseModel):
    days_overdue: int

    outstanding_balance: Decimal = Field(..., decimal_places=2)
    fine_rate: Decimal = Field(..., decimal_places=2)
    monthly_interest_rate: Decimal = Field(..., decimal_places=2)

    fine_amount: Decimal = Field(..., decimal_places=2)
    interest_amount: Decimal = Field(..., decimal_places=2)

    total_updated: Decimal = Field(..., decimal_places=2)
