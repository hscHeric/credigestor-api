"""
Schemas de Usuário - [RF01, RF12]
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Schema base de usuário"""

    name: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    role: UserRole = UserRole.SELLER


class UserCreate(UserBase):
    """Schema para criação de usuário"""

    password: str = Field(..., min_length=6, description="Senha do usuário")


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""

    name: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema de resposta de usuário"""

    id: int
    active: bool
    temporary_password: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema para lista de usuários"""

    users: list[UserResponse]
    total: int
