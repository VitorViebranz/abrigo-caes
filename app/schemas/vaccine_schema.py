from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, model_validator


class VaccineCreateRequest(BaseModel):
    animal_id: int
    name: str
    application_date: date
    next_dose: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def next_dose_must_be_after_application(self):
        if self.next_dose and self.next_dose <= self.application_date:
            raise ValueError("next_dose must be after application_date.")
        return self


class VaccineUpdateRequest(BaseModel):
    name: str | None = None
    application_date: date | None = None
    next_dose: date | None = None
    notes: str | None = None


class VaccineResponse(BaseModel):
    id: int
    animal_id: int
    name: str
    application_date: date
    next_dose: date | None
    notes: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VaccineAlertResponse(BaseModel):
    id: int
    animal_id: int
    animal_name: str
    name: str
    next_dose: date
    status: str
