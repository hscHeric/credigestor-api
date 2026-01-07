from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.dashboard_schema import DashboardOut
from app.services.dashboard_service import get_dashboard

router = APIRouter()


@router.get("", response_model=DashboardOut)
def dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_dashboard(db)
