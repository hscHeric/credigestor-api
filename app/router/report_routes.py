from __future__ import annotations
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.report_schema import DelinquencyReportOut
from app.services.report_service import delinquency_report

router = APIRouter()


@router.get("/delinquency", response_model=DelinquencyReportOut)
def delinquency_report_route(
    due_from: Optional[date] = Query(None),
    due_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Gera o relatório de inadimplência com filtros de datas de vencimento."""
    return delinquency_report(db, due_from=due_from, due_to=due_to)
