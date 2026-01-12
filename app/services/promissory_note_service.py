from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.promissory_note import PromissoryNote
from app.models.sale import Sale


def get_promissory_note_by_id(db: Session, note_id: int) -> PromissoryNote | None:
    """Busca uma promissória pelo ID."""
    return db.query(PromissoryNote).filter(PromissoryNote.id == note_id).first()


def list_promissory_notes(
    db: Session,
    *,
    status: str | None = None,
    customer_id: int | None = None,
    due_from: date | None = None,
    due_to: date | None = None,
) -> dict:
    """
    RF06 - Consultar e Filtrar Promissórias
    """
    q = (
        db.query(PromissoryNote, Sale, Customer)
        .join(Sale, PromissoryNote.sale_id == Sale.id)
        .join(Customer, Sale.customer_id == Customer.id)
    )

    if status:
        q = q.filter(PromissoryNote.status == status)

    if customer_id:
        q = q.filter(Sale.customer_id == customer_id)

    if due_from:
        q = q.filter(PromissoryNote.due_date >= due_from)

    if due_to:
        q = q.filter(PromissoryNote.due_date <= due_to)

    q = q.order_by(PromissoryNote.due_date.asc(), PromissoryNote.id.asc())

    rows = q.all()

    items: list[dict] = []
    for note, sale, customer in rows:
        outstanding = note.original_amount - note.paid_amount

        items.append(
            {
                "id": note.id,
                "sale_id": note.sale_id,
                "customer_id": customer.id,
                "customer_name": customer.full_name,
                "installment_number": note.installment_number,
                "due_date": note.due_date,
                "original_amount": note.original_amount,
                "paid_amount": note.paid_amount,
                "outstanding_balance": outstanding,
                "status": note.status,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            }
        )

    return {
        "items": items,
        "total": len(items),
        "message": (
            "MSG13: Nenhuma promissória encontrada com os filtros aplicados."
            if len(items) == 0
            else None
        ),
    }


def update_promissory_note_status(
    db: Session, promissory_note_id: int, status: str
) -> PromissoryNote:
    """Atualiza o status de uma promissória."""
    note = (
        db.query(PromissoryNote).filter(PromissoryNote.id == promissory_note_id).first()
    )
    if not note:
        raise ValueError("Promissória não encontrada.")

    note.status = status
    db.commit()
    db.refresh(note)
    return note
