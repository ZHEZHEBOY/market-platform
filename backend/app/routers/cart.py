from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartListResponse

router = APIRouter(prefix="/api/cart", tags=["购物车"])


@router.get("", response_model=CartListResponse)
def list_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id)
        .order_by(CartItem.id.desc())
        .all()
    )
    result = []
    total_amount = 0
    for item in items:
        result.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            product_image=item.product.image_url,
            price=item.product.price,
            stock=item.product.stock,
            quantity=item.quantity,
            created_at=item.created_at,
        ))
        total_amount += item.product.price * item.quantity
    return CartListResponse(items=result, total_amount=total_amount)


@router.post("", response_model=CartItemResponse)
def add_to_cart(
    data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == data.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == data.product_id,
    ).first()
    if existing:
        new_qty = existing.quantity + data.quantity
        if new_qty > product.stock:
            raise HTTPException(status_code=400, detail="超出库存")
        existing.quantity = new_qty
        db.commit()
        db.refresh(existing)
        return CartItemResponse(
            id=existing.id,
            product_id=existing.product_id,
            product_name=product.name,
            product_image=product.image_url,
            price=product.price,
            stock=product.stock,
            quantity=existing.quantity,
            created_at=existing.created_at,
        )

    if data.quantity > product.stock:
        raise HTTPException(status_code=400, detail="超出库存")

    cart_item = CartItem(user_id=current_user.id, **data.model_dump())
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.product_id,
        product_name=product.name,
        product_image=product.image_url,
        price=product.price,
        stock=product.stock,
        quantity=cart_item.quantity,
        created_at=cart_item.created_at,
    )


@router.put("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车项不存在")

    if data.quantity > cart_item.product.stock:
        raise HTTPException(status_code=400, detail="超出库存")
    cart_item.quantity = data.quantity
    db.commit()
    db.refresh(cart_item)
    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.product_id,
        product_name=cart_item.product.name,
        product_image=cart_item.product.image_url,
        price=cart_item.product.price,
        stock=cart_item.product.stock,
        quantity=cart_item.quantity,
        created_at=cart_item.created_at,
    )


@router.delete("/{item_id}")
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    db.delete(cart_item)
    db.commit()
    return {"detail": "已移除"}
