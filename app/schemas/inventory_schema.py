from datetime import date, datetime
from pydantic import BaseModel

from models import InventoryMovementType
from .pagination_schema import PaginationInfo


class InventoryItemCreateRequest(BaseModel):
    name: str
    description: str | None = None
    unit: str | None = None


class InventoryItemUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    unit: str | None = None


class InventoryItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    unit: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class InventoryItemListResponse(BaseModel):
    data: list[InventoryItemResponse]
    pagination: PaginationInfo


class InventoryMovementCreateRequest(BaseModel):
    item_id: int
    type: InventoryMovementType
    quantity: float
    date: date
    unit: str | None = None
    note: str | None = None
    reference: str | None = None


class InventoryMovementResponse(BaseModel):
    id: int
    item_id: int
    type: str
    quantity: float
    unit: str | None
    date: date
    note: str | None
    reference: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class StockBalanceResponse(BaseModel):
    item_id: int
    item_name: str
    unit: str | None
    is_active: bool
    balance: float
