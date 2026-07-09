from pydantic import BaseModel, EmailStr, ConfigDict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None

    model_config = ConfigDict(from_attributes=True)