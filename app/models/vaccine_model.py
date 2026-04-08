from datetime import date, datetime, timezone
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from .base_model import BaseModel


class VaccineModel(BaseModel):
    __tablename__ = "vaccines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dog_id = Column(
        Integer, ForeignKey("dogs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(100), nullable=False)
    application_date = Column(Date, nullable=False)
    next_dose = Column(Date, nullable=False)
    notes = Column(String(300), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
