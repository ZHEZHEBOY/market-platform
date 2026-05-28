"""Coupon routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.coupon import Coupon, UserCoupon, CouponStatus
from app.schemas.coupon import CouponCreate, CouponResponse, UserCouponResponse, CouponClaimResponse
from app.dependencies import get_current_user, get_current_admin as get_admin_user

router = APIRouter(prefix="/api/coupons", tags=["coupons"])


@router.get("/available", response_model=List[CouponResponse])
def get_available_coupons(db: Session = Depends(get_db)):
    """获取可领取的优惠券列表"""
    now = datetime.utcnow()
    coupons = db.query(Coupon).filter(
        Coupon.is_active == True,
        Coupon.start_time <= now,
        Coupon.end_time >= now,
    ).all()

    # 过滤已领完的
    result = []
    for c in coupons:
        if c.total_count == 0 or c.used_count < c.total_count:
            result.append(c)

    return result


@router.post("/claim/{coupon_id}", response_model=CouponClaimResponse)
def claim_coupon(coupon_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """领取优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    now = datetime.utcnow()
    if not coupon.is_active or coupon.start_time > now or coupon.end_time < now:
        raise HTTPException(status_code=400, detail="优惠券不可用")

    if coupon.total_count > 0 and coupon.used_count >= coupon.total_count:
        raise HTTPException(status_code=400, detail="优惠券已领完")

    # 检查是否已领取
    existing = db.query(UserCoupon).filter(
        UserCoupon.user_id == current_user.id,
        UserCoupon.coupon_id == coupon_id,
        UserCoupon.status == CouponStatus.ACTIVE
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已领取过该优惠券")

    # 领取
    user_coupon = UserCoupon(
        user_id=current_user.id,
        coupon_id=coupon_id,
        status=CouponStatus.ACTIVE
    )
    coupon.used_count += 1
    db.add(user_coupon)
    db.commit()
    db.refresh(user_coupon)

    return CouponClaimResponse(
        success=True,
        message="领取成功",
        coupon=UserCouponResponse.from_orm(user_coupon)
    )


@router.get("/my", response_model=List[UserCouponResponse])
def get_my_coupons(status: CouponStatus = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取我的优惠券"""
    query = db.query(UserCoupon).filter(UserCoupon.user_id == current_user.id)
    if status:
        query = query.filter(UserCoupon.status == status)
    return query.all()


@router.post("/use/{user_coupon_id}")
def use_coupon(user_coupon_id: int, order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """使用优惠券（下单时调用）"""
    user_coupon = db.query(UserCoupon).filter(
        UserCoupon.id == user_coupon_id,
        UserCoupon.user_id == current_user.id,
        UserCoupon.status == CouponStatus.ACTIVE
    ).first()

    if not user_coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在或已使用")

    coupon = user_coupon.coupon
    now = datetime.utcnow()
    if coupon.end_time < now:
        user_coupon.status = CouponStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=400, detail="优惠券已过期")

    user_coupon.status = CouponStatus.USED
    user_coupon.order_id = order_id
    user_coupon.used_at = now
    db.commit()

    return {"success": True, "message": "优惠券使用成功"}


# ── 管理端 ──

@router.post("/admin/create", response_model=CouponResponse)
def create_coupon(coupon_data: CouponCreate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """创建优惠券（管理员）"""
    # 检查 code 唯一
    existing = db.query(Coupon).filter(Coupon.code == coupon_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="优惠券码已存在")

    coupon = Coupon(**coupon_data.dict())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.get("/admin/list", response_model=List[CouponResponse])
def list_coupons(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取所有优惠券（管理员）"""
    return db.query(Coupon).order_by(Coupon.created_at.desc()).all()


@router.patch("/admin/{coupon_id}/toggle")
def toggle_coupon(coupon_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """启用/禁用优惠券（管理员）"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    coupon.is_active = not coupon.is_active
    db.commit()
    return {"success": True, "is_active": coupon.is_active}


def calculate_discount(coupon: Coupon, amount: int) -> int:
    """计算优惠金额"""
    if amount < coupon.min_amount:
        return 0

    if coupon.coupon_type == "fixed":
        return min(coupon.value, amount)
    else:
        discount = int(amount * coupon.value / 100)
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
        return discount
