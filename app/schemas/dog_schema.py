from datetime import date, datetime
from pydantic import BaseModel
from models import AdoptionStatus, DogSize


class DogCreateRequest(BaseModel):
    name: str
    estimated_age_months: int
    size: DogSize
    entry_date: date
    notes: str | None = None


class DogUpdateRequest(BaseModel):
    name: str | None = None
    estimated_age_months: int | None = None
    size: DogSize | None = None
    notes: str | None = None


class DogStatusUpdateRequest(BaseModel):
    adoption_status: AdoptionStatus


class DogResponse(BaseModel):
    id: int
    name: str
    estimated_age_months: int
    size: str
    adoption_status: str
    entry_date: date
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime | None = None