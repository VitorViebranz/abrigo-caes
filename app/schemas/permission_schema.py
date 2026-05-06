from pydantic import BaseModel, ConfigDict


class PermissionCreateRequest(BaseModel):
    name: str
    description: str | None = None


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
