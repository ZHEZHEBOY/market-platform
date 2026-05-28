from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User, UserRole, Shop
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus

router = APIRouter(prefix="/api/admin", tags=["后台管理"])


@router.get("/dashboard")
def dashboard(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    total_users = db.query(func.count(User.id)).filter(User.role == UserRole.BUYER).scalar()
    total_sellers = db.query(func.count(User.id)).filter(User.role == UserRole.SELLER).scalar()

    today_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= today,
        Order.status != OrderStatus.CANCELLED,
    ).scalar()

    today_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
        Order.created_at >= today,
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED]),
    ).scalar()

    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.PENDING,
    ).scalar()

    pending_shops = db.query(func.count(Shop.id)).filter(Shop.status == "pending").scalar()

    return {
        "total_products": total_products,
        "total_users": total_users,
        "total_sellers": total_sellers,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "pending_orders": pending_orders,
        "pending_shops": pending_shops,
    }


# ── 商家审核 ──────────────────────────────────────────

@router.get("/shops")
def list_shops(
    status: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Shop)
    if status:
        q = q.filter(Shop.status == status)
    total = q.count()
    shops = q.order_by(Shop.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for shop in shops:
        owner = db.query(User).filter(User.id == shop.owner_id).first()
        result.append({
            "id": shop.id,
            "name": shop.name,
            "description": shop.description,
            "logo": shop.logo,
            "status": shop.status,
            "owner_name": owner.username if owner else "未知",
            "owner_email": owner.email if owner else "",
            "created_at": shop.created_at.isoformat() if shop.created_at else None,
        })
    return {"items": result, "total": total, "page": page, "page_size": page_size}


@router.put("/shops/{shop_id}/approve")
def approve_shop(
    shop_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    shop.status = "approved"
    db.commit()
    return {"detail": "已通过审核"}


@router.put("/shops/{shop_id}/reject")
def reject_shop(
    shop_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    shop.status = "rejected"
    db.commit()
    return {"detail": "已拒绝"}
