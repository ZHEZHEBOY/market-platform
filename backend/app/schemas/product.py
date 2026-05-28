import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    price: int = Field(gt=0, le=99999999)  # in cents, max 999,999.99
    original_price: Optional[int] = Field(None, gt=0, le=99999999)
    stock: int = Field(ge=0, le=999999)
    category: str = Field(default="", max_length=50)
    image_url: str = Field(default="", max_length=500)
    images: Optional[list[str]] = None
    specs: Optional[dict] = None
    skus: Optional[list[dict]] = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        # 移除潜在的 XSS 字符
        return re.sub(r'[<>"\']', '', v.strip())

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        # 移除 HTML 标签
        return re.sub(r'<[^>]+>', '', v.strip())


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[int] = Field(None, gt=0)
    original_price: Optional[int] = None
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[list[str]] = None
    specs: Optional[dict] = None
    skus: Optional[list[dict]] = None
    is_active: Optional[bool] = None
    is_new: Optional[bool] = None
    is_hot: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    shop_id: Optional[int] = None
    name: str
    description: str
    price: int
    original_price: Optional[int] = None
    stock: int
    sales: int = 0
    category: str
    image_url: str
    images: Optional[list[str]] = None
    specs: Optional[dict] = None
    skus: Optional[list[dict]] = None
    is_active: bool
    is_new: bool = False
    is_hot: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
