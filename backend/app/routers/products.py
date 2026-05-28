import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import UPLOAD_DIR
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.product import Product
from app.models.order import OrderItem
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse

router = APIRouter(prefix="/api/products", tags=["商品"])


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(""),
    category: str = Query(""),
    min_price: int = Query(None, ge=0),
    max_price: int = Query(None, ge=0),
    sort: str = Query("", pattern="^(price_asc|price_desc|newest|sales)?$"),
    db: Session = Depends(get_db),
):
    q = db.query(Product).filter(Product.is_active == True)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    if category:
        q = q.filter(Product.category == category)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)

    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    elif sort == "newest":
        q = q.order_by(Product.id.desc())
    elif sort == "sales":
        sales_sub = (
            db.query(OrderItem.product_id, func.sum(OrderItem.quantity).label("total_sold"))
            .group_by(OrderItem.product_id)
            .subquery()
        )
        q = q.outerjoin(sales_sub, Product.id == sales_sub.c.product_id).order_by(
            func.coalesce(sales_sub.c.total_sold, 0).desc()
        )
    else:
        q = q.order_by(Product.id.desc())

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(Product.category)
        .filter(Product.is_active == True, Product.category != "")
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.post("", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(product, key, val)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    product.is_active = False
    db.commit()
    return {"detail": "已下架"}


@router.post("/upload")
def upload_image(
    file: UploadFile = File(...),
    admin: dict = Depends(get_current_admin),
):
    ext = os.path.splitext(file.filename or ".jpg")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = Path(UPLOAD_DIR) / filename
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return {"url": f"/uploads/{filename}"}
