from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import require_admin
from app.schemas.system_config_schema import SystemConfigOut, SystemConfigUpdate
from app.services.system_config_service import (
    get_or_create_system_config,
    update_system_config,
)

router = APIRouter()


@router.get("", response_model=SystemConfigOut)
def get_system_config(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return get_or_create_system_config(db)


@router.put("", response_model=SystemConfigOut, status_code=status.HTTP_200_OK)
def put_system_config(
    data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return update_system_config(db, data)

