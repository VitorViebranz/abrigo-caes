import enum
from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel


class FinancialType(str, enum.Enum):
    entrada = "entrada"
    saida   = "saida"


class FinancialCategory(str, enum.Enum):
    # Entradas
    doacao  = "doacao"
    # Saídas
    suprimentos  = "suprimentos"
    veterinario  = "veterinario"
    custos_fixos = "custos_fixos"
    outros       = "outros"


class Financial(BaseModel):
    __tablename__ = "financial"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    type: Mapped[str] = mapped_column(Enum(FinancialType), nullable=False)

    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    date: Mapped[date] = mapped_column(Date, nullable=False)

    category: Mapped[str] = mapped_column(Enum(FinancialCategory), nullable=False)

    description: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Optional — only for donations (entrada)
    donor: Mapped[str | None] = mapped_column(String(150), nullable=True)

    # Business rule: records cannot be deleted, only deactivated
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
