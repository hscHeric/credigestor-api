from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.models.sale import Sale
from app.schemas.sale_schema import SaleCreate, SaleUpdate


TWOPLACES = Decimal("0.01")


def _last_day_of_month(year: int, month: int) -> int:
    """
    Retorna o último dia do mês para um dado ano e mês.
    """
    if month == 2:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        return 29 if is_leap else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def add_months(d: date, months: int) -> date:
    """
    Adiciona meses a uma data, ajustando o dia se necessário.
    """
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(d.day, _last_day_of_month(y, m))
    return date(y, m, day)


def _split_amount(total: Decimal, n: int) -> List[Decimal]:
    """
    Divide total em n parcelas.
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
    """
    Cria uma venda e suas notas promissórias associadas.
    """
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise ValueError(
            "Cliente não encontrado. Verifique ou cadastre um novo cliente."
        )

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
    db.flush()

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


def get_sales(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    user_id: int = None,
    client_name: str = None,
) -> List[Sale]:
    """
    Lista vendas com paginação e filtros opcionais.
    """
    query = db.query(Sale)

    if user_id:
        query = query.filter(Sale.user_id == user_id)
    
    if client_name:
        query = query.join(Customer).filter(Customer.full_name.ilike(f"%{client_name}%"))

    return query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()


def get_sale_by_id(db: Session, sale_id: int) -> Sale | None:
    return db.query(Sale).filter(Sale.id == sale_id).first()


def delete_sale(db: Session, sale_id: int) -> bool:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        return False
    db.delete(sale)
    db.commit()
    return True


def update_sale(
    db: Session, 
    sale_id: int, 
    data: SaleUpdate
) -> Tuple[Sale, List[PromissoryNote]]:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise ValueError("Venda não encontrada.")

    financial_changes = (
        (data.total_amount is not None and data.total_amount != sale.total_amount) or
        (data.installments_count is not None and data.installments_count != sale.installments_count) or
        (data.first_installment_date is not None and data.first_installment_date != sale.first_installment_date) or
        (data.down_payment is not None and data.down_payment != sale.down_payment)
    )

    if financial_changes:
        existing_notes = db.query(PromissoryNote).filter(PromissoryNote.sale_id == sale.id).all()
        for note in existing_notes:
            if note.status == PromissoryNoteStatus.PAID.value or note.paid_amount > 0:
                raise ValueError("Não é possível alterar valores de uma venda que já possui parcelas pagas.")

        if data.total_amount: sale.total_amount = data.total_amount
        if data.down_payment: sale.down_payment = data.down_payment
        if data.installments_count: sale.installments_count = data.installments_count
        if data.first_installment_date: sale.first_installment_date = data.first_installment_date
        
        db.query(PromissoryNote).filter(PromissoryNote.sale_id == sale.id).delete()

        financed = (sale.total_amount - sale.down_payment).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        amounts = _split_amount(financed, sale.installments_count)

        new_notes = []
        for i in range(1, sale.installments_count + 1):
            due = add_months(sale.first_installment_date, i - 1)
            pn = PromissoryNote(
                sale_id=sale.id,
                installment_number=i,
                original_amount=amounts[i - 1],
                paid_amount=Decimal("0.00"),
                due_date=due,
                status=PromissoryNoteStatus.PENDING.value
            )
            db.add(pn)
            new_notes.append(pn)
    else:
        if data.description is not None:
            sale.description = data.description
        if data.customer_id is not None:
            sale.customer_id = data.customer_id
    
    db.commit()
    db.refresh(sale)
    
    current_notes = db.query(PromissoryNote).filter(PromissoryNote.sale_id == sale.id).all()
    return sale, current_notes