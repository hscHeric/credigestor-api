from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models.user import User
from app.router.auth_routes import require_admin
from app.services.backup_service import build_backup_zip

router = APIRouter()


@router.get(
    "", summary="Gerar e baixar backup dos dados (ZIP com CSV)", status_code=200
)
def download_backup(
    db: Session = Depends(get_db),  # mantém padrão do projeto
    _: User = Depends(require_admin),
):
    try:
        filename, zip_bytes = build_backup_zip(engine, schema="public")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MSG21: Erro ao gerar o arquivo de backup. {str(e)}",
        )

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
