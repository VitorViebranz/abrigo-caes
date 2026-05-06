from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from models.animal_model import AnimalModel
from .base_model import BaseModel


class VaccineModel(BaseModel):
    __tablename__ = "vaccines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    animal_id = Column(
        Integer, ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(100), nullable=False)
    application_date = Column(Date, nullable=False)
    next_dose = Column(Date, nullable=True)
    notes = Column(String(300), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    animal: Mapped["AnimalModel"] = relationship("AnimalModel", back_populates="vaccines")