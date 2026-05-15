from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus

router = APIRouter(prefix="/api/admin", tags=["后台管理"])


@router.get("/dashboard")
def dashboard(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    total_users = db.query(func.count(User.id)).filter(User.role == UserRole.USER).scalar()

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

    top_products = (
        db.query(
            Product.id, Product.name,
            func.sum(OrderItem.quantity * OrderItem.price_at_time).label("sales"),
            func.sum(OrderItem.quantity).label("qty")
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.created_at >= today,
            Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED])
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity * OrderItem.price_at_time).desc())
        .limit(5).all()
    )

    return {
        "total_products": total_products,
        "total_users": total_users,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "pending_orders": pending_orders,
        "top_products": [{"id": p.id, "name": p.name, "sales": p.sales, "qty": p.qty} for p in top_products],
    }
