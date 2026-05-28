"""Analytics routes for admin dashboard."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, Shop
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.dependencies import get_admin_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/sales-trend")
def get_sales_trend(days: int = 30, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取销售趋势（最近N天）"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # 按天统计销售额和订单数
    results = db.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('total_amount'),
        func.count(Order.id).label('order_count')
    ).filter(
        Order.created_at >= start_date,
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED])
    ).group_by(
        func.date(Order.created_at)
    ).order_by('date').all()

    return {
        "dates": [str(r.date) for r in results],
        "amounts": [r.total_amount or 0 for r in results],
        "counts": [r.order_count for r in results]
    }


@router.get("/user-growth")
def get_user_growth(days: int = 30, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取用户增长趋势"""
    start_date = datetime.utcnow() - timedelta(days=days)

    results = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date
    ).group_by(
        func.date(User.created_at)
    ).order_by('date').all()

    return {
        "dates": [str(r.date) for r in results],
        "counts": [r.count for r in results]
    }


@router.get("/order-status")
def get_order_status_distribution(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取订单状态分布"""
    results = db.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()

    return {
        "statuses": [r.status.value for r in results],
        "counts": [r.count for r in results]
    }


@router.get("/category-sales")
def get_category_sales(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取分类销售排行"""
    results = db.query(
        Product.category,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.price_at_time * OrderItem.quantity).label('total_amount')
    ).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED])
    ).group_by(
        Product.category
    ).order_by(
        func.sum(OrderItem.price_at_time * OrderItem.quantity).desc()
    ).limit(10).all()

    return {
        "categories": [r.category for r in results],
        "quantities": [r.total_quantity for r in results],
        "amounts": [r.total_amount or 0 for r in results]
    }


@router.get("/top-products")
def get_top_products(limit: int = 10, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取热销商品排行"""
    results = db.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.price_at_time * OrderItem.quantity).label('total_amount')
    ).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED])
    ).group_by(
        Product.id, Product.name
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(limit).all()

    return {
        "products": [r.name for r in results],
        "quantities": [r.total_quantity for r in results],
        "amounts": [r.total_amount or 0 for r in results]
    }


@router.get("/overview")
def get_overview(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """获取总览数据"""
    total_users = db.query(func.count(User.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED])
    ).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar()
    total_shops = db.query(func.count(Shop.id)).scalar()

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_products": total_products,
        "total_shops": total_shops
    }
