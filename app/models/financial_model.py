import enum
from datetime import date, datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, Numeric, String
from .base_model import BaseModel


class FinancialType(str, enum.Enum):
    entrada = "entrada"
    saida   = "saida"


class FinancialCategory(str, enum.Enum):
    doacao  = "doacao"
    suprimentos = "suprimentos"
    veterinario = "veterinario"
    custos_fixos = "custos_fixos"
    outros = "outros"


class FinancialModel(BaseModel):
    __tablename__ = "financial"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(FinancialType), nullable=False)
    value = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    category = Column(Enum(FinancialCategory), nullable=False)
    description = Column(String(300), nullable=True)
    donor = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
