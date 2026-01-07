from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.models.sale import Sale


def delinquency_report(db: Session) -> dict:
    today = date.today()

    # pega promissórias vencidas e não pagas
    rows = (
        db.query(PromissoryNote, Sale, Customer)
        .join(Sale, PromissoryNote.sale_id == Sale.id)
        .join(Customer, Sale.customer_id == Customer.id)
        .filter(PromissoryNote.due_date < today)
        .filter(PromissoryNote.status != PromissoryNoteStatus.PAID.value)
        .order_by(Customer.full_name.asc(), PromissoryNote.due_date.asc())
        .all()
    )

    by_customer: dict[int, dict] = {}

    for note, sale, customer in rows:
        cust_id = customer.id
        if cust_id not in by_customer:
            by_customer[cust_id] = {
                "customer_id": cust_id,
                "customer_name": customer.full_name,
                "customer_phone": customer.phone,
                "installments": [],
                "total_due": Decimal("0.00"),
            }

        outstanding = note.original_amount - note.paid_amount
        days_overdue = (today - note.due_date).days if today > note.due_date else 0

        by_customer[cust_id]["installments"].append(
            {
                "promissory_note_id": note.id,
                "sale_id": sale.id,
                "due_date": note.due_date,
                "days_overdue": days_overdue,
                "original_amount": note.original_amount,
                "paid_amount": note.paid_amount,
                "outstanding_balance": outstanding,
                "status": note.status,
            }
        )
        by_customer[cust_id]["total_due"] = (
            by_customer[cust_id]["total_due"] + outstanding
        )

    customers = []
    total_due_all = Decimal("0.00")

    for cust in by_customer.values():
        cust["overdue_installments_count"] = len(cust["installments"])
        total_due_all += cust["total_due"]
        customers.append(cust)

    return {
        "customers": customers,
        "total_customers": len(customers),
        "total_due_all": total_due_all,
    }
