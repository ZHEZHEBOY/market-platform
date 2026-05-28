"""Coupon schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.coupon import CouponType, CouponStatus


class CouponCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    coupon_type: CouponType
    value: int
    min_amount: int = 0
    max_discount: Optional[int] = None
    total_count: int = 0
    start_time: datetime
    end_time: datetime


class CouponResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    coupon_type: CouponType
    value: int
    min_amount: int
    max_discount: Optional[int]
    total_count: int
    used_count: int
    start_time: datetime
    end_time: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserCouponResponse(BaseModel):
    id: int
    coupon: CouponResponse
    status: CouponStatus
    received_at: datetime
    used_at: Optional[datetime]

    class Config:
        from_attributes = True


class CouponClaimResponse(BaseModel):
    success: bool
    message: str
    coupon: Optional[UserCouponResponse] = None
