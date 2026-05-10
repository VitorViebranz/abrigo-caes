from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .inventory_model import InventoryItemModel


class DonationModel(BaseModel):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    donor = Column(String(150), nullable=True)
    date = Column(Date, nullable=False)
    monetary_value = Column(Numeric(10, 2), nullable=True)
    description = Column(String(300), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    items: Mapped[list["DonationItemModel"]] = relationship(
        "DonationItemModel",
        back_populates="donation",
        cascade="all, delete-orphan",
    )


class DonationItemModel(BaseModel):
    __tablename__ = "donation_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    donation_id = Column(Integer, ForeignKey("donations.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(30), nullable=True)

    donation: Mapped["DonationModel"] = relationship("DonationModel", back_populates="items")
    item: Mapped["InventoryItemModel"] = relationship("InventoryItemModel")
