from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel


class Vaccine(BaseModel):
    __tablename__ = "vaccines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    dog_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dogs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    application_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Business rule: vaccines must always have a next_dose date
    next_dose: Mapped[date] = mapped_column(Date, nullable=False)

    notes: Mapped[str | None] = mapped_column(String(300), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
