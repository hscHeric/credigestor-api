from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import require_admin
from app.schemas.user_schema import UserCreate, UserOut, UserUpdate
from app.services.user_service import (
    create_user,
    list_users,
    update_user,
    deactivate_user,
)

router = APIRouter()


@router.get("", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return list_users(db)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_route(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserOut)
def update_user_route(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return update_user(db, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return deactivate_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
