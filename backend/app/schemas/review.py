from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    order_item_id: int
    rating: int = Field(ge=1, le=5)
    content: str = ""
    images: str = ""  # JSON array of image URLs


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    order_item_id: int
    rating: int
    content: str
    images: str
    username: str = ""
    avatar: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    avg_rating: float = 0.0
    page: int
    page_size: int
