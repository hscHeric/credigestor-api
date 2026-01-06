"""
Schemas base para responses comuns
"""

from pydantic import BaseModel
from datetime import datetime


class MessageResponse(BaseModel):
    """Response padrão para mensagens"""

    message: str


class ErrorResponse(BaseModel):
    """Response padrão para erros"""

    detail: str


class TimestampSchema(BaseModel):
    """Schema base com timestamps"""

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
