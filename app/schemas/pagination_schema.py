from typing import Optional

from pydantic import BaseModel, Field, model_validator


class PaginationInfo(BaseModel):
    # canonical fields used across the app
    total_count: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    current_page: int = Field(ge=1)
    total_pages: int = Field(ge=0)

    # legacy/alternate names accepted from services; converted before validation
    actual_page: Optional[int] = None
    per_page: Optional[int] = None
    max_allowed_per_page: Optional[int] = None
    total_items: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_fields(cls, values: dict) -> dict:
        # map alternate keys to canonical ones when provided
        if values is None:
            return values
        if "total_count" not in values and "total_items" in values:
            values["total_count"] = values.get("total_items")
        if "limit" not in values and "per_page" in values:
            values["limit"] = values.get("per_page")
        if "current_page" not in values and "actual_page" in values:
            values["current_page"] = values.get("actual_page")
        if "offset" not in values:
            # derive offset from actual_page and per_page when possible
            ap = values.get("actual_page")
            pp = values.get("per_page")
            if ap is not None and pp is not None:
                try:
                    values["offset"] = (int(ap) - 1) * int(pp)
                except Exception:
                    pass
        return values
