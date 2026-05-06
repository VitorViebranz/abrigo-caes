from pydantic import BaseModel, ConfigDict


class RoleCreateRequest(BaseModel):
    name: str
    permissions: list[str] = []


class RoleUpdateRequest(BaseModel):
    permissions: list[str] | None = None


class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: list[str] = []

    model_config = ConfigDict(from_attributes=True)
