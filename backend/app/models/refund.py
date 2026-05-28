"""Refund models."""
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class RefundStatus(str, enum.Enum):
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    REFUNDED = "refunded"  # 已退款
    CANCELLED = "cancelled"  # 已取消


class RefundReason(str, enum.Enum):
    QUALITY = "quality"  # 质量问题
    WRONG_ITEM = "wrong_item"  # 发错商品
    NOT_AS_DESCRIBED = "not_as_described"  # 与描述不符
    CHANGE_MIND = "change_mind"  # 不想要了
    SIZE_ISSUE = "size_issue"  # 尺码不合适
    OTHER = "other"  # 其他


class Refund(Base):
    """退款/退货申请"""
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(SQLEnum(RefundReason), nullable=False)
    description = Column(Text)
    amount = Column(Integer, nullable=False)  # 退款金额(分)
    status = Column(SQLEnum(RefundStatus), default=RefundStatus.PENDING)
    admin_note = Column(Text)  # 管理员备注
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    order = relationship("Order")
    order_item = relationship("OrderItem")
    user = relationship("User")
