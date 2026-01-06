"""
Dependencies para injeção de dependência do FastAPI
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_access_token

# Security scheme para autenticação Bearer
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Obtém o usuário atual a partir do token JWT

    Args:
        credentials: Credenciais do header Authorization
        db: Sessão do banco de dados

    Returns:
        Usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou usuário não encontrado
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta está inativa. Entre em contato com o administrador.",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica se o usuário está ativo
    """
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica se o usuário é administrador

    Args:
        current_user: Usuário atual

    Returns:
        Usuário se for admin

    Raises:
        HTTPException: Se o usuário não for admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar este recurso.",
        )
    return current_user
