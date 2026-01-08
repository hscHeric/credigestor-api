from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.interest_schema import InterestFineBreakdown
from app.models.promissory_note import PromissoryNote
from app.services.interest_service import calculate_interest_and_fine_for_note

router = APIRouter()


@router.get(
    "/promissory-notes/{note_id}/interest", response_model=InterestFineBreakdown
)
def preview_interest(
    note_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    note = db.query(PromissoryNote).filter(PromissoryNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Promissória não encontrada")

    return calculate_interest_and_fine_for_note(db, note=note)
