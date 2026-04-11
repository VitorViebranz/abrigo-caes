import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, relationship
from .base_model import BaseModel

if TYPE_CHECKING:
    from .vaccine_model import VaccineModel


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
    estimated_age = Column(Float, nullable=False)
    size = Column(Enum(DogSize), nullable=False)
    adoption_status = Column(
        Enum(AdoptionStatus),
        nullable=False,
        default=AdoptionStatus.disponivel,
    )
    entry_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String(500), nullable=True)

    neutered = Column(Boolean, default=False, nullable=False)
    dewormed = Column(Boolean, default=False, nullable=False)
    socializes_with_other_dogs = Column(Boolean, default=False, nullable=False)
    color = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    vaccines: Mapped[list["VaccineModel"]] = relationship(
        "VaccineModel", back_populates="dog", cascade="all, delete-orphan"
    )