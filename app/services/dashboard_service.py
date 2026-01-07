from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.models.sale import Sale


def _d0(v) -> Decimal:
    return Decimal(v or 0)


def get_dashboard(db: Session) -> dict:
    today = date.today()
    start_30d = today - timedelta(days=30)

    # total_to_receive = soma do saldo (original - pago) das promissórias NÃO quitadas
    total_to_receive = (
        db.query(
            func.coalesce(
                func.sum(PromissoryNote.original_amount - PromissoryNote.paid_amount), 0
            )
        )
        .filter(PromissoryNote.status != PromissoryNoteStatus.PAID.value)
        .scalar()
    )

    # total_overdue = saldo das promissórias vencidas (due_date < hoje) e não pagas
    total_overdue = (
        db.query(
            func.coalesce(
                func.sum(PromissoryNote.original_amount - PromissoryNote.paid_amount), 0
            )
        )
        .filter(PromissoryNote.due_date < today)
        .filter(PromissoryNote.status != PromissoryNoteStatus.PAID.value)
        .scalar()
    )

    # received_last_30_days = soma do total_amount (principal + juros + multa) nos últimos 30 dias
    received_last_30_days = (
        db.query(
            func.coalesce(
                func.sum(
                    Payment.amount_paid + Payment.interest_amount + Payment.fine_amount
                ),
                0,
            )
        )
        .filter(Payment.payment_date >= start_30d)
        .filter(Payment.payment_date <= today)
        .scalar()
    )

    # próximas 5 a vencer (não pagas), ordenadas por vencimento asc
    # precisamos do customer_id -> join Sale
    next_due_rows = (
        db.query(PromissoryNote, Sale.customer_id)
        .join(Sale, PromissoryNote.sale_id == Sale.id)
        .filter(PromissoryNote.status != PromissoryNoteStatus.PAID.value)
        .order_by(PromissoryNote.due_date.asc(), PromissoryNote.id.asc())
        .limit(5)
        .all()
    )

    next_due = []
    for note, customer_id in next_due_rows:
        outstanding = note.original_amount - note.paid_amount
        next_due.append(
            {
                "promissory_note_id": note.id,
                "sale_id": note.sale_id,
                "customer_id": int(customer_id),
                "due_date": note.due_date,
                "original_amount": note.original_amount,
                "paid_amount": note.paid_amount,
                "outstanding_balance": outstanding,
                "status": note.status,
            }
        )

    return {
        "total_to_receive": _d0(total_to_receive),
        "total_overdue": _d0(total_overdue),
        "received_last_30_days": _d0(received_last_30_days),
        "next_due": next_due,
    }
