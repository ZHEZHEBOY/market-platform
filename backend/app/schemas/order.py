from datetime import datetime

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    address_id: int
    cart_item_ids: list[int]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price_at_time: int

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    order_no: str
    total_amount: int
    status: str
    address_snapshot: dict
    items: list[OrderItemResponse] = []
    created_at: datetime
    paid_at: datetime | None = None

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int
