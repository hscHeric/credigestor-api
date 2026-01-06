"""
Service de Autenticação
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.security import verify_password, create_access_token


class AuthService:
    """Service para autenticação de usuários"""

    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> TokenResponse:
        """
        Autentica usuário e retorna token JWT

        Args:
            db: Sessão do banco de dados
            login_data: Dados de login (email e senha)

        Returns:
            Token de acesso com informações do usuário

        Raises:
            HTTPException: Se credenciais inválidas ou conta inativa
        """
        # MSG02: "E-mail ou senha incorretos. Por favor, tente novamente."
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos. Por favor, tente novamente.",
            )

        # MSG04: "Sua conta está inativa. Entre em contato com o administrador."
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sua conta está inativa. Entre em contato com o administrador.",
            )

        # Criar token JWT - usar role como string
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role}
        )

        # MSG01: "Login realizado com sucesso."
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            user_name=user.name,
            user_role=user.role,
        )
