from datetime import datetime

from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    product_name: str = ""
    product_price: int = 0
    product_image: str = ""
    product_desc: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


class FavoriteListResponse(BaseModel):
    items: list[FavoriteResponse]
    total: int
    page: int
    page_size: int
