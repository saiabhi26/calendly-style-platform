from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    name: str
    slug: str
    timezone: str = "UTC"


class OrganizationUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    timezone: str
    plan: str

    model_config = ConfigDict(from_attributes=True)