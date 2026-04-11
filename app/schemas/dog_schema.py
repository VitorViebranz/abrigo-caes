from datetime import date, datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from models import AdoptionStatus, DogSize
from .vaccine_schema import VaccineResponse


class DogVaccineCreateRequest(BaseModel):
    name: str
    application_date: date
    next_dose: date | None = None
    notes: str | None = None


class DogCreateRequest(BaseModel):
    name: str
    estimated_age: int
    size: DogSize
    entry_date: date
    notes: str | None = None
    neutered: bool = False
    dewormed: bool = False
    socializes_with_other_dogs: bool = False
    color: str | None = None
    vaccines: list[DogVaccineCreateRequest] = Field(default_factory=list)


class DogUpdateRequest(BaseModel):
    name: str | None = None
    estimated_age: int | None = None
    size: DogSize | None = None
    notes: str | None = None
    neutered: bool | None = None
    dewormed: bool | None = None
    socializes_with_other_dogs: bool | None = None
    color: str | None = None


class DogStatusUpdateRequest(BaseModel):
    adoption_status: AdoptionStatus


class DogResponse(BaseModel):
    id: int
    name: str
    estimated_age: float
    vaccines: List[VaccineResponse] = []
    size: str
    adoption_status: str
    entry_date: date
    is_active: bool
    notes: str | None
    neutered: bool
    dewormed: bool
    socializes_with_other_dogs: bool
    color: str | None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)