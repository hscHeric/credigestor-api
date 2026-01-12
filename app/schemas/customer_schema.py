from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, validator

from app.schemas.base import TimestampSchema

CPF_REGEX = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")


class CustomerBase(BaseModel):
    full_name: str = Field(..., max_length=200)
    cpf: str = Field(..., description="CPF (apenas números ou com pontuação)")
    phone: str = Field(..., max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    active: bool = True

    @field_validator("cpf")
    @classmethod
    def validate_cpf_format(cls, v: str) -> str:
        digits = re.sub(r"[^0-9]", "", v)

        if len(digits) != 11:
            raise ValueError("CPF deve conter 11 dígitos.")

        return digits


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    active: Optional[bool] = None


class CustomerOut(BaseModel):
    id: int
    full_name: str
    cpf: str
    email: Optional[str] = None 
    phone: str

    # formata o CPF para exibição no frontend
    @validator('cpf', pre=True, check_fields=False)
    def format_cpf_from_db(cls, v):
        if isinstance(v, str) and len(v) == 11 and v.isdigit():
            return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
        return v
    
    model_config = ConfigDict(from_attributes=True)
