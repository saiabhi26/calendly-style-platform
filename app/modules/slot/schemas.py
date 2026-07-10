from datetime import datetime
from pydantic import BaseModel


class SlotResponse(BaseModel):
    start: datetime
    end: datetime

