from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import (
    authenticate_user,
    create_access_token,
    decode_access_token,
)

router = APIRouter()
security = HTTPBearer(description="Use: Bearer <JWT>")


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    return {
        "access_token": access_token,
        "user_id": user.id,
        "user_name": user.name,
        "user_role": user.role,
    }


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

    # injeta role do token
    user.token_role = role
    return user


def require_admin(user: User = Depends(get_current_user)):
    if user.token_role != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return user


def require_seller(user: User = Depends(get_current_user)):
    if user.token_role != "seller":
        raise HTTPException(status_code=403, detail="Acesso restrito a vendedores")
    return user


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.token_role,
    }
