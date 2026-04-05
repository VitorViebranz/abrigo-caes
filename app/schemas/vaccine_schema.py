from datetime import date, datetime
from pydantic import BaseModel, model_validator


class VaccineCreateRequest(BaseModel):
    dog_id: int
    name: str
    application_date: date
    next_dose: date
    notes: str | None = None

    @model_validator(mode="after")
    def next_dose_must_be_after_application(self):
        if self.next_dose <= self.application_date:
            raise ValueError("next_dose must be after application_date.")
        return self


class VaccineUpdateRequest(BaseModel):
    name: str | None = None
    application_date: date | None = None
    next_dose: date | None = None
    notes: str | None = None


class VaccineResponse(BaseModel):
    id: int
    dog_id: int
    name: str
    application_date: date
    next_dose: date
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class VaccineAlertResponse(BaseModel):
    """Used in the alert endpoints (overdue / due soon)."""
    id: int
    dog_id: int
    dog_name: str  # Populated by the service layer
    name: str
    next_dose: date
    status: str    # "overdue" | "due_soon"
