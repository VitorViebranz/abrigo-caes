import json
from datetime import date, datetime
from typing import List

from fastapi import Form, HTTPException, status
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


class AnimalCreateForm(BaseModel):
    name: str
    estimated_age: float
    size: str
    species: str
    entry_date: str
    notes: str | None = None
    neutered: bool = False
    dewormed: bool = False
    socializes_with_other_animals: bool = False
    color: str | None = None
    microchipped: bool = False
    vaccines: str | None = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        estimated_age: float = Form(...),
        size: str = Form(...),
        species: str = Form(...),
        entry_date: str = Form(...),
        notes: str | None = Form(None),
        neutered: bool = Form(False),
        dewormed: bool = Form(False),
        socializes_with_other_animals: bool = Form(False),
        color: str | None = Form(None),
        microchipped: bool = Form(False),
        vaccines: str | None = Form(None),
    ) -> "AnimalCreateForm":
        return cls(
            name=name,
            estimated_age=estimated_age,
            size=size,
            species=species,
            entry_date=entry_date,
            notes=notes,
            neutered=neutered,
            dewormed=dewormed,
            socializes_with_other_animals=socializes_with_other_animals,
            color=color,
            microchipped=microchipped,
            vaccines=vaccines,
        )

    def to_request(self) -> "AnimalCreateRequest":
        vaccine_items: list[dict] = []
        if self.vaccines:
            try:
                parsed = json.loads(self.vaccines)
                if isinstance(parsed, list):
                    vaccine_items = parsed
                else:
                    raise ValueError("vaccines must be a list")
            except (ValueError, json.JSONDecodeError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid vaccines payload: {exc}",
                )

        return AnimalCreateRequest.model_validate({
            "name": self.name,
            "estimated_age": self.estimated_age,
            "size": self.size,
            "species": self.species,
            "entry_date": self.entry_date,
            "notes": self.notes,
            "neutered": self.neutered,
            "dewormed": self.dewormed,
            "socializes_with_other_animals": self.socializes_with_other_animals,
            "color": self.color,
            "microchipped": self.microchipped,
            "vaccines": vaccine_items,
        })


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
    image_path: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)