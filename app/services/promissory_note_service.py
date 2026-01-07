from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.promissory_note import PromissoryNote


def get_promissory_note_by_id(db: Session, note_id: int) -> PromissoryNote | None:
    return db.query(PromissoryNote).filter(PromissoryNote.id == note_id).first()


def list_promissory_notes(
    db: Session,
    *,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
) -> list[PromissoryNote]:
    q = db.query(PromissoryNote)

    if status:
        q = q.filter(PromissoryNote.status == status)

    if due_date_from:
        q = q.filter(PromissoryNote.due_date >= due_date_from)

    if due_date_to:
        q = q.filter(PromissoryNote.due_date <= due_date_to)

    if customer_id:
        # join com sales para filtrar por cliente
        from app.models.sale import Sale

        q = q.join(Sale, PromissoryNote.sale_id == Sale.id).filter(
            Sale.customer_id == customer_id
        )

    return q.order_by(PromissoryNote.due_date.asc(), PromissoryNote.id.asc()).all()
