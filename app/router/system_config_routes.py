from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.promissory_note_schema import PromissoryNoteListResponse
from app.services.promissory_note_service import list_promissory_notes

router = APIRouter()


@router.get("", response_model=PromissoryNoteListResponse)
def get_promissory_notes(
    status: Optional[str] = Query(default=None),
    customer_id: Optional[int] = Query(default=None, ge=1),
    due_from: Optional[date] = Query(default=None),
    due_to: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list_promissory_notes(
        db,
        status=status,
        customer_id=customer_id,
        due_from=due_from,
        due_to=due_to,
    )
