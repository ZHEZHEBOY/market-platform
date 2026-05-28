import os
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.config import UPLOAD_DIR
from app.database import get_db
from app.dependencies import get_current_seller
from app.models.user import User, Shop
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.shop import ShopCreate, ShopUpdate, ShopResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse

router = APIRouter(prefix="/api/seller", tags=["卖家中心"])


def _get_shop(user: User, db: Session) -> Shop:
    shop = db.query(Shop).filter(Shop.owner_id == user.id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return shop


# ── 店铺管理 ──────────────────────────────────────────

@router.get("/shop", response_model=ShopResponse)
def get_my_shop(current_user: User = Depends(get_current_seller), db: Session = Depends(get_db)):
    return _get_shop(current_user, db)


@router.put("/shop", response_model=ShopResponse)
def update_my_shop(
    data: ShopUpdate,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(shop, key, val)
    db.commit()
    db.refresh(shop)
    return shop


# ── 卖家商品管理 ──────────────────────────────────────

@router.get("/products", response_model=ProductListResponse)
def list_my_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    q = db.query(Product).filter(Product.shop_id == shop.id)
    total = q.count()
    items = q.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/products", response_model=ProductResponse)
def create_my_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    if shop.status != "approved":
        raise HTTPException(status_code=403, detail="店铺未审核通过，无法上架商品")
    product = Product(**data.model_dump(), shop_id=shop.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_my_product(
    product_id: int,
    data: ProductUpdate,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(product, key, val)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def delete_my_product(
    product_id: int,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    product.is_active = False
    db.commit()
    return {"detail": "已下架"}


@router.post("/products/upload")
def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_seller),
):
    ext = os.path.splitext(file.filename or ".jpg")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = Path(UPLOAD_DIR) / filename
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return {"url": f"/uploads/{filename}"}


# ── 卖家订单管理 ──────────────────────────────────────

@router.get("/orders")
def list_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(""),
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    shop_product_ids = [p.id for p in db.query(Product.id).filter(Product.shop_id == shop.id).all()]
    if not shop_product_ids:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    q = (
        db.query(Order)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(OrderItem.product_id.in_(shop_product_ids))
        .distinct()
    )
    if status:
        q = q.filter(Order.status == status)

    total = q.count()
    orders = q.options(joinedload(Order.items)).order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for order in orders:
        my_items = [item for item in order.items if item.product_id in shop_product_ids]
        result.append({
            "id": order.id,
            "order_no": order.order_no,
            "total_amount": sum(i.price_at_time * i.quantity for i in my_items),
            "status": order.status.value if hasattr(order.status, 'value') else order.status,
            "address_snapshot": order.address_snapshot,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product.name if item.product else "未知商品",
                    "quantity": item.quantity,
                    "price_at_time": item.price_at_time,
                }
                for item in my_items
            ],
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        })

    return {"items": result, "total": total, "page": page, "page_size": page_size}


@router.put("/orders/{order_id}/ship")
def ship_my_order(
    order_id: int,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="只能对已支付订单发货")

    shop_product_ids = [p.id for p in db.query(Product.id).filter(Product.shop_id == shop.id).all()]
    order_product_ids = [item.product_id for item in order.items]
    if not any(pid in shop_product_ids for pid in order_product_ids):
        raise HTTPException(status_code=403, detail="该订单不包含您的商品")

    order.status = OrderStatus.SHIPPED
    db.commit()
    return {"detail": "已发货"}


# ── 卖家数据统计 ──────────────────────────────────────

@router.get("/dashboard")
def seller_dashboard(
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    shop = _get_shop(current_user, db)
    shop_product_ids = [p.id for p in db.query(Product.id).filter(Product.shop_id == shop.id).all()]

    total_products = db.query(Product).filter(Product.shop_id == shop.id, Product.is_active == True).count()

    if not shop_product_ids:
        return {
            "shop_name": shop.name,
            "shop_status": shop.status,
            "total_products": 0,
            "total_orders": 0,
            "total_revenue": 0,
            "today_orders": 0,
            "today_revenue": 0,
            "pending_orders": 0,
        }

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_orders = (
        db.query(func.count(func.distinct(Order.id)))
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(OrderItem.product_id.in_(shop_product_ids), Order.status != OrderStatus.CANCELLED)
        .scalar()
    )

    total_revenue = (
        db.query(func.sum(OrderItem.price_at_time * OrderItem.quantity))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(OrderItem.product_id.in_(shop_product_ids), Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED]))
        .scalar()
    ) or 0

    today_orders = (
        db.query(func.count(func.distinct(Order.id)))
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(OrderItem.product_id.in_(shop_product_ids), Order.created_at >= today_start, Order.status != OrderStatus.CANCELLED)
        .scalar()
    )

    today_revenue = (
        db.query(func.sum(OrderItem.price_at_time * OrderItem.quantity))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(OrderItem.product_id.in_(shop_product_ids), Order.created_at >= today_start, Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.SIGNED]))
        .scalar()
    ) or 0

    pending_orders = (
        db.query(func.count(func.distinct(Order.id)))
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(OrderItem.product_id.in_(shop_product_ids), Order.status == OrderStatus.PAID)
        .scalar()
    )

    return {
        "shop_name": shop.name,
        "shop_status": shop.status,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "pending_orders": pending_orders,
    }
