from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class BookingCreate(BaseModel):
    service_id: int
    slot_start: datetime
    customer_name: str
    customer_email: EmailStr


class BookingResponse(BaseModel):
    id: int
    service_id: int
    slot_start: datetime
    slot_end: datetime
    customer_name: str
    customer_email: EmailStr
    status: str

    model_config = ConfigDict(from_attributes=True)

