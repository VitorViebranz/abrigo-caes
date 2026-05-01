from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    user_email: str
    role: str


class UserCreateRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "voluntario"


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    role: str | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)