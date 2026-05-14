import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .donation_model import DonationItemModel


class InventoryMovementType(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"


class InventoryItemModel(BaseModel):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    description = Column(String(300), nullable=True)
    unit = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    movements: Mapped[list["InventoryMovementModel"]] = relationship(
        "InventoryMovementModel",
        back_populates="item",
        cascade="all, delete-orphan",
    )


class InventoryMovementModel(BaseModel):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    type = Column(Enum(InventoryMovementType), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(30), nullable=True)
    date = Column(Date, nullable=False)
    note = Column(String(300), nullable=True)
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    item: Mapped["InventoryItemModel"] = relationship("InventoryItemModel", back_populates="movements")
