import enum
from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, String
from .base_model import BaseModel


class DogSize(str, enum.Enum):
    P = "P"
    M = "M"
    G = "G"


class AdoptionStatus(str, enum.Enum):
    disponivel = "disponivel"
    em_processo = "em_processo"
    adotado = "adotado"


class DogModel(BaseModel):
    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    estimated_age_months = Column(Integer, nullable=False)
    size = Column(Enum(DogSize), nullable=False)
    adoption_status = Column(
        Enum(AdoptionStatus),
        nullable=False,
        default=AdoptionStatus.disponivel,
    )
    entry_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
