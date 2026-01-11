from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user

from app.models.customer import Customer
from app.services.export_service import to_csv_bytes
from app.services.promissory_note_service import list_promissory_notes

router = APIRouter()


@router.get("/promissory-notes/export.csv")
def export_promissory_notes_csv(
    status: Optional[str] = Query(default=None),
    customer_id: Optional[int] = Query(default=None, ge=1),
    due_from: Optional[date] = Query(default=None),
    due_to: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    RF13 - Exportar promissórias (CSV), respeitando filtros do RF06.
    """
    result = list_promissory_notes(
        db,
        status=status,
        customer_id=customer_id,
        due_from=due_from,
        due_to=due_to,
    )

    headers = [
        "id",
        "sale_id",
        "customer_id",
        "customer_name",
        "installment_number",
        "due_date",
        "original_amount",
        "paid_amount",
        "outstanding_balance",
        "status",
        "created_at",
        "updated_at",
    ]

    csv_bytes = to_csv_bytes(headers=headers, rows=result["items"])

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="promissorias.csv"',
        },
    )


@router.get("/customers/export.csv")
def export_customers_csv(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    RF13 - Exportar clientes (CSV).
    """
    customers = db.query(Customer).order_by(Customer.id.asc()).all()

    rows = [
        {
            "id": c.id,
            "full_name": c.full_name,
            "cpf": c.cpf,
            "phone": c.phone,
            "email": c.email,
            "address": c.address,
            "active": c.active,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in customers
    ]

    headers = [
        "id",
        "full_name",
        "cpf",
        "phone",
        "email",
        "address",
        "active",
        "created_at",
        "updated_at",
    ]

    csv_bytes = to_csv_bytes(headers=headers, rows=rows)

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="clientes.csv"',
        },
    )
