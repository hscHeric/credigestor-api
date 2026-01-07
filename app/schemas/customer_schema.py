from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.schemas.base import TimestampSchema

CPF_REGEX = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")


class CustomerBase(BaseModel):
    full_name: str = Field(..., max_length=200)
    cpf: str = Field(..., description="Formato XXX.XXX.XXX-XX")
    phone: str = Field(..., max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    active: bool = True

    @field_validator("cpf")
    @classmethod
    def validate_cpf_format(cls, v: str) -> str:
        if not CPF_REGEX.match(v):
            raise ValueError("CPF deve estar no formato XXX.XXX.XXX-XX")
        return v


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    active: Optional[bool] = None


class CustomerOut(CustomerBase, TimestampSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
