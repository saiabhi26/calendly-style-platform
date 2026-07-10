from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    organization_id: int
    title: str
    duration_minutes: int
    price: Decimal = Decimal("0")
    mode: Literal["ONLINE", "OFFLINE"] = "OFFLINE"


class ServiceUpdate(BaseModel):
    title: str | None = None
    duration_minutes: int | None = None
    price: Decimal | None = None
    mode: Literal["ONLINE", "OFFLINE"] | None = None


class ServiceResponse(BaseModel):
    id: int
    organization_id: int
    title: str
    duration_minutes: int
    price: Decimal
    mode: str

    model_config = ConfigDict(from_attributes=True)