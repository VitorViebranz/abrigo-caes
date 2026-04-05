from datetime import date, datetime
from pydantic import BaseModel
from models import FinancialCategory, FinancialType


class FinancialCreateRequest(BaseModel):
    type: FinancialType
    value: float
    date: date
    category: FinancialCategory
    description: str | None = None
    donor: str | None = None  # Only relevant for type=entrada


class FinancialResponse(BaseModel):
    id: int
    type: str
    value: float
    date: date
    category: str
    description: str | None
    donor: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    total_income: float
    total_expenses: float
    balance: float
    records: list[FinancialResponse]
