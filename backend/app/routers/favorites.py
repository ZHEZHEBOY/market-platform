from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.models.product import Product
from app.schemas.favorite import FavoriteResponse, FavoriteListResponse

router = APIRouter(prefix="/api/favorites", tags=["收藏"])


@router.get("", response_model=FavoriteListResponse)
def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Favorite).filter(Favorite.user_id == current_user.id)
    total = q.count()
    favs = q.order_by(Favorite.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for fav in favs:
        product = db.query(Product).filter(Product.id == fav.product_id).first()
        result.append(FavoriteResponse(
            id=fav.id,
            user_id=fav.user_id,
            product_id=fav.product_id,
            product_name=product.name if product else "未知商品",
            product_price=product.price if product else 0,
            product_image=product.image_url if product else "",
            product_desc=product.description if product else "",
            created_at=fav.created_at,
        ))
    return FavoriteListResponse(items=result, total=total, page=page, page_size=page_size)


@router.post("/{product_id}")
def add_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    existing = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.product_id == product_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="已收藏")
    fav = Favorite(user_id=current_user.id, product_id=product_id)
    db.add(fav)
    db.commit()
    return {"detail": "已收藏"}


@router.delete("/{product_id}")
def remove_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.product_id == product_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="未收藏")
    db.delete(fav)
    db.commit()
    return {"detail": "已取消收藏"}


@router.get("/check/{product_id}")
def check_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.product_id == product_id).first()
    return {"favorited": existing is not None}
