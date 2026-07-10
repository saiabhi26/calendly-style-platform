from datetime import time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AvailabilityRuleCreate(BaseModel):
    organization_id: int
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def check_time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AvailabilityRuleResponse(BaseModel):
    id: int
    organization_id: int
    day_of_week: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)