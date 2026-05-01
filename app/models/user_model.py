from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from .base_model import BaseModel

import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    voluntario = "voluntario"
    financeiro = "financeiro"


class UserModel(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.voluntario)
    token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
