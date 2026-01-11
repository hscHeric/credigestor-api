from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.services.payment_receipt_service import build_payment_receipt_pdf

router = APIRouter()


@router.get("/payments/{payment_id}/receipt.pdf")
def get_payment_receipt_pdf(
    payment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    pdf = build_payment_receipt_pdf(db, payment_id=payment_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado.")

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="recibo_pagamento_{payment_id}.pdf"'
        },
    )
