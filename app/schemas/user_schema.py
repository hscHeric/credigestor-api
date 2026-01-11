from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.schemas.base import TimestampSchema

UserRole = Literal["admin", "seller"]


class UserOut(TimestampSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    active: bool


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    role: UserRole = "seller"
    active: bool = True
    # senha NÃO vem do admin: será definida automaticamente como o e-mail


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    role: Optional[UserRole] = None
    active: Optional[bool] = None

    # opcional: permitir resetar senha para o e-mail
    reset_password_to_email: Optional[bool] = False
