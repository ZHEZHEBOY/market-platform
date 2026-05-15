from datetime import datetime

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: str
    price: int  # in cents
    stock: int
    quantity: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CartListResponse(BaseModel):
    items: list[CartItemResponse]
    total_amount: int  # in cents
