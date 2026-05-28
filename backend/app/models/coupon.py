"""Coupon models."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class CouponType(str, enum.Enum):
    FIXED = "fixed"  # 固定金额
    PERCENT = "percent"  # 百分比折扣


class CouponStatus(str, enum.Enum):
    ACTIVE = "active"  # 可用
    USED = "used"  # 已使用
    EXPIRED = "expired"  # 已过期


class Coupon(Base):
    """优惠券模板"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    coupon_type = Column(SQLEnum(CouponType), nullable=False)
    value = Column(Integer, nullable=False)  # 固定金额(分) 或 百分比(1-100)
    min_amount = Column(Integer, default=0)  # 最低消费金额(分)
    max_discount = Column(Integer)  # 最大优惠金额(分)，仅百分比类型
    total_count = Column(Integer, default=0)  # 发放总量，0表示不限
    used_count = Column(Integer, default=0)  # 已领取数量
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user_coupons = relationship("UserCoupon", back_populates="coupon")


class UserCoupon(Base):
    """用户领取的优惠券"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # 使用的订单
    status = Column(SQLEnum(CouponStatus), default=CouponStatus.ACTIVE)
    received_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)

    # 关系
    coupon = relationship("Coupon", back_populates="user_coupons")
    user = relationship("User")
    order = relationship("Order")
