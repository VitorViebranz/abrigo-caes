from pydantic import BaseModel, Field


class PaginationInfo(BaseModel):
    total_count: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    current_page: int = Field(ge=1)
    total_pages: int = Field(ge=0)
