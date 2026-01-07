from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.payment_schema import PaymentCreate, PaymentOut
from app.services.payment_service import register_payment

router = APIRouter()


@router.post(
    "/promissory-notes/{promissory_note_id}/payments",
    response_model=PaymentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    promissory_note_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return register_payment(db, promissory_note_id=promissory_note_id, data=data)
    except ValueError as e:
        msg = str(e)
        if "não encontrada" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
