import enum
from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel


class DogSize(str, enum.Enum):
    P = "P"
    M = "M"
    G = "G"


class AdoptionStatus(str, enum.Enum):
    disponivel  = "disponivel"
    em_processo = "em_processo"
    adotado     = "adotado"


class Dog(BaseModel):
    __tablename__ = "dogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Estimated age in months for precision (e.g. 6 months, 18 months)
    estimated_age_months: Mapped[int] = mapped_column(Integer, nullable=False)

    size: Mapped[str] = mapped_column(Enum(DogSize), nullable=False)

    adoption_status: Mapped[str] = mapped_column(
        Enum(AdoptionStatus),
        nullable=False,
        default=AdoptionStatus.disponivel,
    )

    entry_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Soft delete — only admins can deactivate
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
