from typing import Any
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
    permissions: list[str] | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    role: str | None = None
    permissions: list[str] | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    is_active: bool
    role: str 
    permissions: list[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v: Any) -> str:
        if hasattr(v, "name"):
            return v.name
        return v

    @field_validator("permissions", mode="before")
    @classmethod
    def extract_permissions(cls, v: Any, info):
        if v is not None:
            return v
        role = None
        if hasattr(info, "data") and isinstance(info.data, dict):
            role = info.data.get("role")
        if role and hasattr(role, "permissions"):
            return [p.name for p in role.permissions]
        return []