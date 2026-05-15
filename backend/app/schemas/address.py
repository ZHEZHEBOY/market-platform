from datetime import datetime

from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    receiver_name: str = Field(max_length=50)
    phone: str = Field(max_length=20)
    province: str = Field(max_length=50)
    city: str = Field(max_length=50)
    district: str = Field(max_length=50)
    detail: str = Field(max_length=200)
    is_default: bool = False


class AddressUpdate(BaseModel):
    receiver_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    province: str | None = Field(None, max_length=50)
    city: str | None = Field(None, max_length=50)
    district: str | None = Field(None, max_length=50)
    detail: str | None = Field(None, max_length=200)
    is_default: bool | None = None


class AddressResponse(BaseModel):
    id: int
    receiver_name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}
