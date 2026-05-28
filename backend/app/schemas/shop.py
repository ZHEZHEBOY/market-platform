from datetime import datetime

from pydantic import BaseModel, Field


class ShopCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = ""


class ShopUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    logo: str | None = None


class ShopResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str
    logo: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
