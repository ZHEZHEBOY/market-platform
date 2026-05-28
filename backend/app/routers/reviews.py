import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.review import Review
from app.models.product import Product
from app.models.order import OrderItem, Order, OrderStatus
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewListResponse

router = APIRouter(prefix="/api/reviews", tags=["评价"])


@router.post("", response_model=ReviewResponse)
def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_item = db.query(OrderItem).filter(OrderItem.id == data.order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="订单项不存在")
    order = db.query(Order).filter(Order.id == order_item.order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=403, detail="无权评价此订单")
    if order.status not in (OrderStatus.SHIPPED, OrderStatus.SIGNED):
        raise HTTPException(status_code=400, detail="只能评价已发货或已签收的订单")
    existing = db.query(Review).filter(Review.order_item_id == data.order_item_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该商品已评价")
    review = Review(
        user_id=current_user.id,
        product_id=order_item.product_id,
        order_item_id=data.order_item_id,
        rating=data.rating,
        content=data.content,
        images=data.images,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        product_id=review.product_id,
        order_item_id=review.order_item_id,
        rating=review.rating,
        content=review.content,
        images=review.images,
        username=current_user.username,
        avatar=current_user.avatar,
        created_at=review.created_at,
    )


@router.get("/product/{product_id}", response_model=ReviewListResponse)
def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(Review).filter(Review.product_id == product_id)
    total = q.count()
    avg_rating = db.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar() or 0.0
    reviews = q.order_by(Review.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for r in reviews:
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append(ReviewResponse(
            id=r.id,
            user_id=r.user_id,
            product_id=r.product_id,
            order_item_id=r.order_item_id,
            rating=r.rating,
            content=r.content,
            images=r.images,
            username=user.username if user else "匿名",
            avatar=user.avatar if user else None,
            created_at=r.created_at,
        ))
    return ReviewListResponse(items=result, total=total, avg_rating=round(avg_rating, 1), page=page, page_size=page_size)


@router.get("/my")
def get_my_reviewable_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reviewed_item_ids = [r.order_item_id for r in db.query(Review.order_item_id).filter(Review.user_id == current_user.id).all()]
    items = (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.user_id == current_user.id,
            Order.status.in_([OrderStatus.SHIPPED, OrderStatus.SIGNED]),
            ~OrderItem.id.in_(reviewed_item_ids) if reviewed_item_ids else True,
        )
        .all()
    )
    result = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        result.append({
            "order_item_id": item.id,
            "order_id": item.order_id,
            "product_id": item.product_id,
            "product_name": product.name if product else "未知商品",
            "product_image": product.image_url if product else "",
            "quantity": item.quantity,
            "price_at_time": item.price_at_time,
        })
    return result


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    if review.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="无权删除此评价")
    db.delete(review)
    db.commit()
    return {"detail": "已删除"}
