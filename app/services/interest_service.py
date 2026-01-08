from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from datetime import date

from sqlalchemy.orm import Session

from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.services.system_config_service import get_or_create_system_config

TWOPLACES = Decimal("0.01")


def _q2(v: Decimal) -> Decimal:
    return v.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def calculate_interest_and_fine_for_note(
    db: Session,
    *,
    note: PromissoryNote,
    on_date: date | None = None,
) -> dict:
    cfg = get_or_create_system_config(db)
    today = on_date or date.today()

    outstanding = _q2(note.original_amount - note.paid_amount)

    # se está quitada ou não tem saldo, nada a calcular
    if note.status == PromissoryNoteStatus.PAID.value or outstanding <= Decimal("0.00"):
        return {
            "days_overdue": 0,
            "outstanding_balance": outstanding,
            "fine_rate": _q2(cfg.fine_rate),
            "monthly_interest_rate": _q2(cfg.monthly_interest_rate),
            "fine_amount": Decimal("0.00"),
            "interest_amount": Decimal("0.00"),
            "total_updated": outstanding,
        }

    days_overdue = 0
    if today > note.due_date:
        days_overdue = (today - note.due_date).days

    if days_overdue <= 0:
        return {
            "days_overdue": 0,
            "outstanding_balance": outstanding,
            "fine_rate": _q2(cfg.fine_rate),
            "monthly_interest_rate": _q2(cfg.monthly_interest_rate),
            "fine_amount": Decimal("0.00"),
            "interest_amount": Decimal("0.00"),
            "total_updated": outstanding,
        }

    fine_amount = _q2(outstanding * (cfg.fine_rate / Decimal("100")))
    # juros mensal proporcional por dias (dias/30)
    interest_amount = _q2(
        outstanding
        * (cfg.monthly_interest_rate / Decimal("100"))
        * (Decimal(days_overdue) / Decimal("30"))
    )

    total_updated = _q2(outstanding + fine_amount + interest_amount)

    return {
        "days_overdue": days_overdue,
        "outstanding_balance": outstanding,
        "fine_rate": _q2(cfg.fine_rate),
        "monthly_interest_rate": _q2(cfg.monthly_interest_rate),
        "fine_amount": fine_amount,
        "interest_amount": interest_amount,
        "total_updated": total_updated,
    }
