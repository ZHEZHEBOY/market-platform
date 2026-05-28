from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse, OrderListResponse
from app.services.order_service import create_order, OrderCreationError
from app.routers.notifications import create_notification

router = APIRouter(prefix="/api/orders", tags=["订单"])


@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Order).filter(Order.user_id == current_user.id)
    if status:
        q = q.filter(Order.status == status)
    total = q.count()
    orders = q.options(joinedload(Order.items)).order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return OrderListResponse(items=orders, total=total, page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).options(joinedload(Order.items)).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("", response_model=OrderResponse)
def place_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        order = create_order(db, current_user, data.address_id, data.cart_item_ids)
    except OrderCreationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order


@router.put("/{order_id}/cancel")
def cancel_order(
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
        raise HTTPException(status_code=400, detail="只能取消待支付订单")

    # Restore stock
    for item in order.items:
        db.query(Product).filter(Product.id == item.product_id).update(
            {"stock": Product.stock + item.quantity}, synchronize_session=False
        )

    order.status = OrderStatus.CANCELLED
    db.commit()

    # 发送取消通知
    create_notification(
        db, current_user.id,
        title="订单已取消",
        content=f"订单 {order.order_no} 已成功取消",
        notification_type="order",
        link=f"/order/{order.id}",
    )

    return {"detail": "已取消"}


# Admin routes
@router.get("/admin/all", response_model=OrderListResponse)
def admin_list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(""),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    total = q.count()
    orders = q.options(joinedload(Order.items)).order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return OrderListResponse(items=orders, total=total, page=page, page_size=page_size)


@router.put("/admin/{order_id}/ship")
def ship_order(
    order_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="只能对已支付订单发货")
    order.status = OrderStatus.SHIPPED
    db.commit()

    # 发送发货通知
    create_notification(
        db, order.user_id,
        title="订单已发货",
        content=f"订单 {order.order_no} 已发货，请注意查收",
        notification_type="order",
        link=f"/order/{order.id}",
    )

    return {"detail": "已发货"}
