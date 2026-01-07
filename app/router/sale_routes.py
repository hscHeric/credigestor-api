from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.sale_schema import SaleCreate, SaleWithNotesOut
from app.services.sale_service import create_sale_and_promissory_notes

router = APIRouter()


@router.post(
    "",
    response_model=SaleWithNotesOut,
    status_code=status.HTTP_201_CREATED,
)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        sale, notes = create_sale_and_promissory_notes(db, user_id=user.id, data=data)
        # Injeta relação no retorno
        sale.promissory_notes = notes
        return sale
    except ValueError as e:
        msg = str(e)
        # Cliente não encontrado -> 404
        if "Cliente não encontrado" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
