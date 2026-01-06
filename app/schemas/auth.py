"""
Schemas de Autenticação
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request de login"""

    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, description="Senha do usuário")


class TokenResponse(BaseModel):
    """Response com token de acesso"""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str
    user_role: str


class ChangePasswordRequest(BaseModel):
    """Request para troca de senha"""

    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
