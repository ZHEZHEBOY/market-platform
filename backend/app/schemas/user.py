from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    avatar: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    avatar: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
