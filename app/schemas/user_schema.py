from datetime import datetime
from alembic.environment import Any
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


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
    is_active: bool
    role: str 

    model_config = ConfigDict(from_attributes=True)

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v: Any) -> str:
        if hasattr(v, "name"):
            return v.name
        return v