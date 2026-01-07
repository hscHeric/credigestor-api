from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class OverdueInstallmentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    promissory_note_id: int
    sale_id: int

    due_date: date
    days_overdue: int

    original_amount: Decimal = Field(..., decimal_places=2)
    paid_amount: Decimal = Field(..., decimal_places=2)
    outstanding_balance: Decimal = Field(..., decimal_places=2)

    status: str


class DelinquentCustomerItem(BaseModel):
    customer_id: int
    customer_name: str
    customer_phone: str | None = None

    overdue_installments_count: int
    total_due: Decimal = Field(..., decimal_places=2)

    installments: List[OverdueInstallmentItem]


class DelinquencyReportOut(BaseModel):
    customers: List[DelinquentCustomerItem]
    total_customers: int
    total_due_all: Decimal = Field(..., decimal_places=2)
