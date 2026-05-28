"""Refund routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus
from app.models.refund import Refund, RefundStatus
from app.schemas.refund import RefundCreate, RefundResponse, RefundReview
from app.dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/api/refunds", tags=["refunds"])


@router.post("/create", response_model=RefundResponse)
def create_refund(data: RefundCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """申请退款/退货"""
    # 验证订单
    order = db.query(Order).filter(
        Order.id == data.order_id,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 验证订单项
    order_item = db.query(OrderItem).filter(
        OrderItem.id == data.order_item_id,
        OrderItem.order_id == data.order_id
    ).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="订单项不存在")

    # 检查是否已申请
    existing = db.query(Refund).filter(
        Refund.order_item_id == data.order_item_id,
        Refund.status.in_([RefundStatus.PENDING, RefundStatus.APPROVED])
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已申请过退款")

    # 计算退款金额
    refund_amount = order_item.price_at_time * order_item.quantity

    refund = Refund(
        order_id=data.order_id,
        order_item_id=data.order_item_id,
        user_id=current_user.id,
        reason=data.reason,
        description=data.description,
        amount=refund_amount,
        status=RefundStatus.PENDING
    )
    db.add(refund)
    db.commit()
    db.refresh(refund)
    return refund


@router.get("/my", response_model=List[RefundResponse])
def get_my_refunds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取我的退款申请"""
    return db.query(Refund).filter(Refund.user_id == current_user.id).order_by(Refund.created_at.desc()).all()


@router.post("/cancel/{refund_id}")
def cancel_refund(refund_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """取消退款申请"""
    refund = db.query(Refund).filter(
        Refund.id == refund_id,
        Refund.user_id == current_user.id,
        Refund.status == RefundStatus.PENDING
    ).first()
    if not refund:
        raise HTTPException(status_code=404, detail="退款申请不存在或已处理")

    refund.status = RefundStatus.CANCELLED
    db.commit()
    return {"success": True, "message": "已取消"}


# ── 管理端 ──

@router.get("/admin/list", response_model=List[RefundResponse])
def list_refunds(status: RefundStatus = None, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取所有退款申请（管理员）"""
    query = db.query(Refund)
    if status:
        query = query.filter(Refund.status == status)
    return query.order_by(Refund.created_at.desc()).all()


@router.patch("/admin/{refund_id}/review", response_model=RefundResponse)
def review_refund(refund_id: int, data: RefundReview, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """审核退款申请（管理员）"""
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="退款申请不存在")

    if refund.status != RefundStatus.PENDING:
        raise HTTPException(status_code=400, detail="该申请已处理")

    if data.status not in [RefundStatus.APPROVED, RefundStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="无效状态")

    refund.status = data.status
    refund.admin_note = data.admin_note

    # 如果通过，更新订单项状态
    if data.status == RefundStatus.APPROVED:
        # 可以在这里添加退款逻辑
        pass

    db.commit()
    db.refresh(refund)
    return refund
