from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.schemas.payment_schema import PaymentCreate


TWOPLACES = Decimal("0.01")


def _q2(v: Decimal) -> Decimal:
    return v.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def register_payment(
    db: Session,
    *,
    promissory_note_id: int,
    data: PaymentCreate,
) -> Payment:
    note = (
        db.query(PromissoryNote).filter(PromissoryNote.id == promissory_note_id).first()
    )

    if not note:
        raise ValueError("Promissória não encontrada")

    if note.status == PromissoryNoteStatus.PAID.value:
        raise ValueError("MSG11: Esta parcela já consta como paga no sistema.")

    outstanding = _q2(note.original_amount - note.paid_amount)
    amount_paid = _q2(data.amount_paid)

    if amount_paid <= Decimal("0.00"):
        raise ValueError("Valor pago deve ser maior que zero.")

    # RF10: pagamento parcial permitido, mas não pode exceder saldo (evita overpay)
    if amount_paid > outstanding:
        raise ValueError("MSG18: O valor pago não pode ser maior que o saldo devedor.")

    payment = Payment(
        promissory_note_id=note.id,
        amount_paid=amount_paid,
        payment_date=data.payment_date,
        interest_amount=_q2(data.interest_amount),
        fine_amount=_q2(data.fine_amount),
        notes=data.notes,
    )

    # Atualiza promissória
    note.paid_amount = _q2(note.paid_amount + amount_paid)

    new_outstanding = _q2(note.original_amount - note.paid_amount)

    if new_outstanding == Decimal("0.00"):
        note.status = PromissoryNoteStatus.PAID.value
        note.payment_date = data.payment_date
    else:
        note.status = PromissoryNoteStatus.PARTIAL_PAYMENT.value
        note.payment_date = None  # ainda não quitou

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
