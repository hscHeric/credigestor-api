from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    decode_access_token,
)

router = APIRouter()

security = HTTPBearer(description="Use: Bearer <JWT>")


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # MSG03: campos obrigatórios (o Pydantic já valida, mas isso cobre o requisito)
    if not data.email or not data.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="MSG03: Por favor, preencha todos os campos obrigatórios.",
        )

    user = authenticate_user(db, data.email, data.password)

    # MSG02: credenciais inválidas (mensagem genérica)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MSG02: E-mail ou senha incorretos. Por favor, tente novamente.",
        )

    # MSG04: usuário inativo/bloqueado
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MSG04: Sua conta está inativa. Entre em contato com o administrador.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        message="MSG01: Login realizado com sucesso. Redirecionando...",
        user_id=user.id,
        user_name=user.name,
        user_role=user.role,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    setattr(user, "token_role", role)
    return user


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": getattr(user, "token_role", user.role),
    }
