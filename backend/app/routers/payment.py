from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.services.alipay_service import create_page_pay_url, verify_notify, query_payment
from app.utils import now_utc

router = APIRouter(prefix="/api/payment", tags=["支付"])


@router.get("/pay/{order_id}")
def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="订单状态不允许支付")

    pay_url = create_page_pay_url(
        order_no=order.order_no,
        total_amount=order.total_amount,
        subject=f"订单-{order.order_no}",
    )
    return {"pay_url": pay_url}


@router.get("/return")
def payment_return(request: Request, db: Session = Depends(get_db)):
    """Sync return from Alipay after user completes payment."""
    params = dict(request.query_params)
    out_trade_no = params.get("out_trade_no")
    if not out_trade_no:
        raise HTTPException(status_code=400, detail="缺少订单号")
    return {"order_no": out_trade_no, "msg": "支付结果请查看订单状态"}


@router.post("/notify")
async def payment_notify(request: Request, db: Session = Depends(get_db)):
    """Async notify from Alipay."""
    data = dict(await request.form())
    if not verify_notify(data.copy()):
        return "fail"

    out_trade_no = data.get("out_trade_no")
    trade_status = data.get("trade_status")

    if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        order = db.query(Order).filter(Order.order_no == out_trade_no).first()
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.PAID
            order.paid_at = now_utc()
            db.commit()
    return "success"


@router.get("/query/{order_id}")
def query_order_payment(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually query payment status from Alipay (dev fallback)."""
    order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    result = query_payment(order.order_no)

    if result and result.get("code") == "10000":
        trade_status = result.get("trade_status")
        if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            if order.status == OrderStatus.PENDING:
                order.status = OrderStatus.PAID
                order.paid_at = now_utc()
                db.commit()
            return {"order_no": order.order_no, "status": order.status.value, "paid": True}

    return {"order_no": order.order_no, "status": order.status.value, "paid": False}
