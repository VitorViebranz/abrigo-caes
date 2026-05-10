from datetime import date, datetime
from pydantic import BaseModel, Field


class DonationItemCreateRequest(BaseModel):
    item_id: int
    quantity: float
    unit: str | None = None


class DonationCreateRequest(BaseModel):
    donor: str | None = None
    date: date
    monetary_value: float | None = None
    description: str | None = None
    items: list[DonationItemCreateRequest] = Field(default_factory=list)


class DonationItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: float
    unit: str | None

    class Config:
        from_attributes = True


class DonationResponse(BaseModel):
    id: int
    donor: str | None
    date: date
    monetary_value: float | None
    description: str | None
    is_active: bool
    created_at: datetime
    items: list[DonationItemResponse]

    class Config:
        from_attributes = True
