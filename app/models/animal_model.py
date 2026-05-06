import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, relationship
from .base_model import BaseModel

if TYPE_CHECKING:
    from .vaccine_model import VaccineModel


class AnimalSize(str, enum.Enum):
    P = "P"
    M = "M"
    G = "G"


class AdoptionStatus(str, enum.Enum):
    disponivel = "disponivel"
    em_processo = "em_processo"
    adotado = "adotado"


class AnimalType(str, enum.Enum):
    dog = "dog"
    cat = "cat"


class AnimalModel(BaseModel):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    estimated_age = Column(Float, nullable=False)
    size = Column(Enum(AnimalSize), nullable=False)
    species = Column(Enum(AnimalType), nullable=False)
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
    socializes_with_other_animals = Column(Boolean, default=False, nullable=False)
    color = Column(String(50), nullable=True)
    microchipped = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    vaccines: Mapped[list["VaccineModel"]] = relationship(
        "VaccineModel", back_populates="animal", cascade="all, delete-orphan"
    )