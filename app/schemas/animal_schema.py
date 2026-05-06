from datetime import date, datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from models import AdoptionStatus, AnimalSize, AnimalType
from .vaccine_schema import VaccineResponse


class AnimalVaccineCreateRequest(BaseModel):
    name: str
    application_date: date
    next_dose: date | None = None
    notes: str | None = None


class AnimalCreateRequest(BaseModel):
    name: str
    estimated_age: int
    size: AnimalSize
    species: AnimalType
    entry_date: date
    notes: str | None = None
    neutered: bool = False
    dewormed: bool = False
    socializes_with_other_animals: bool = False
    color: str | None = None
    microchipped: bool = False
    vaccines: list[AnimalVaccineCreateRequest] = Field(default_factory=list)


class AnimalUpdateRequest(BaseModel):
    name: str | None = None
    estimated_age: int | None = None
    size: AnimalSize | None = None
    species: AnimalType | None = None
    notes: str | None = None
    neutered: bool | None = None
    dewormed: bool | None = None
    socializes_with_other_animals: bool | None = None
    color: str | None = None
    microchipped: bool | None = None


class AnimalStatusUpdateRequest(BaseModel):
    adoption_status: AdoptionStatus


class AnimalResponse(BaseModel):
    id: int
    name: str
    estimated_age: float
    vaccines: List[VaccineResponse] = []
    size: str
    species: str
    adoption_status: str
    entry_date: date
    is_active: bool
    notes: str | None
    neutered: bool
    dewormed: bool
    socializes_with_other_animals: bool
    color: str | None
    microchipped: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)