"""
Endpoints de Autenticação
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, ChangePasswordRequest
from app.schemas.base import MessageResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user
from app.utils.security import verify_password, hash_password
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    [RF01] Autenticar Usuário - LOGIN

    Fluxo Principal:
    1. Usuário fornece e-mail e senha
    2. Sistema valida credenciais
    3. Retorna token JWT se válido

    Mensagens:
    - MSG01: Login realizado com sucesso
    - MSG02: E-mail ou senha incorretos
    - MSG04: Conta inativa
    """
    return AuthService.authenticate_user(db, login_data)


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trocar senha do usuário autenticado

    Args:
        password_data: Senha atual e nova senha
        current_user: Usuário autenticado
        db: Sessão do banco

    Returns:
        Mensagem de sucesso
    """
    # Verificar senha atual
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta."
        )

    # Atualizar senha
    current_user.password_hash = hash_password(password_data.new_password)
    current_user.temporary_password = False

    db.commit()

    return MessageResponse(message="Senha alterada com sucesso.")


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado

    Args:
        current_user: Usuário autenticado

    Returns:
        Informações do usuário
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "active": current_user.active,
        "temporary_password": current_user.temporary_password,
    }

