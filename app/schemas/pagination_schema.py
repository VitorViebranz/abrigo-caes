from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(20, ge=1)


class PaginationInfo(BaseModel):
    actual_page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    total_records: int = Field(ge=0)
