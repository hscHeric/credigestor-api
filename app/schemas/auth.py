from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    """Response com token de acesso"""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str
    user_role: str


class LoginRequest(BaseModel):
    """Request de login"""

    email: EmailStr
    password: str
