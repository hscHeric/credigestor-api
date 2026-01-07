from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.report_schema import DelinquencyReportOut
from app.services.report_service import delinquency_report

router = APIRouter()


@router.get("/delinquency", response_model=DelinquencyReportOut)
def report_delinquency(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return delinquency_report(db)
