from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(max_length=200)
    description: str = ""
    price: int = Field(gt=0)  # in cents
    stock: int = Field(ge=0)
    category: str = ""
    image_url: str = ""


class ProductUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    price: int | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category: str | None = None
    image_url: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    stock: int
    category: str
    image_url: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
