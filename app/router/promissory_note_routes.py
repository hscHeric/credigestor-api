from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.promissory_note_schema import PromissoryNoteOut
from app.services.promissory_note_service import (
    get_promissory_note_by_id,
    list_promissory_notes,
)

router = APIRouter()


@router.get("", response_model=list[PromissoryNoteOut])
def list_all(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list_promissory_notes(
        db,
        status=status,
        customer_id=customer_id,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
    )


@router.get("/{note_id}", response_model=PromissoryNoteOut)
def get_one(
    note_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    note = get_promissory_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Promissória não encontrada")
    return note
