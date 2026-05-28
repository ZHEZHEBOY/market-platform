"""Refund schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.refund import RefundStatus, RefundReason


class RefundCreate(BaseModel):
    order_id: int
    order_item_id: int
    reason: RefundReason
    description: Optional[str] = None


class RefundResponse(BaseModel):
    id: int
    order_id: int
    order_item_id: int
    user_id: int
    reason: RefundReason
    description: Optional[str]
    amount: int
    status: RefundStatus
    admin_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RefundReview(BaseModel):
    status: RefundStatus  # approved 或 rejected
    admin_note: Optional[str] = None
