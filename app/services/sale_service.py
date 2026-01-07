from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.models.sale import Sale
from app.schemas.sale_schema import SaleCreate


TWOPLACES = Decimal("0.01")


def _last_day_of_month(year: int, month: int) -> int:
    # fevereiro
    if month == 2:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        return 29 if is_leap else 28
    # meses 30 dias
    if month in (4, 6, 9, 11):
        return 30
    return 31


def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(d.day, _last_day_of_month(y, m))
    return date(y, m, day)


def _split_amount(total: Decimal, n: int) -> List[Decimal]:
    """
    Divide total em n parcelas, garantindo:
    - 2 casas decimais
    - soma exata == total
    Ajuste de centavos fica na última parcela.
    """
    total = total.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    base = (total / Decimal(n)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    parts = [base] * n
    diff = total - sum(parts)
    parts[-1] = (parts[-1] + diff).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    return parts


def create_sale_and_promissory_notes(
    db: Session,
    *,
    user_id: int,
    data: SaleCreate,
) -> Tuple[Sale, List[PromissoryNote]]:
    # Cliente existe?
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise ValueError(
            "Cliente não encontrado. Verifique ou cadastre um novo cliente."
        )

    # validações de negócio
    if data.installments_count <= 0:
        raise ValueError("MSG09: O número de parcelas deve ser maior que zero.")

    if data.down_payment > data.total_amount:
        raise ValueError("Entrada não pode ser maior que o valor total.")

    financed = (data.total_amount - data.down_payment).quantize(
        TWOPLACES, rounding=ROUND_HALF_UP
    )

    sale = Sale(
        customer_id=data.customer_id,
        user_id=user_id,
        description=data.description,
        total_amount=data.total_amount,
        down_payment=data.down_payment,
        installments_count=data.installments_count,
        first_installment_date=data.first_installment_date,
    )
    db.add(sale)
    db.flush()  # obtém sale.id sem commit

    amounts = _split_amount(financed, data.installments_count)

    notes: List[PromissoryNote] = []
    for i in range(1, data.installments_count + 1):
        due = add_months(data.first_installment_date, i - 1)
        pn = PromissoryNote(
            sale_id=sale.id,
            installment_number=i,
            original_amount=amounts[i - 1],
            paid_amount=Decimal("0.00"),
            due_date=due,
            payment_date=None,
            status=PromissoryNoteStatus.PENDING.value,
            notes=None,
        )
        db.add(pn)
        notes.append(pn)

    db.commit()
    db.refresh(sale)
    for pn in notes:
        db.refresh(pn)

    return sale, notes
