from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartItem
from app.models.product import Product
from app.models.address import Address
from app.utils import generate_order_no, now_utc


class OrderCreationError(Exception):
    pass


def create_order(db: Session, user: User, address_id: int, cart_item_ids: list[int]) -> Order:
    # Validate address
    address = db.query(Address).filter(
        Address.id == address_id, Address.user_id == user.id
    ).first()
    if not address:
        raise OrderCreationError("地址不存在")

    # Validate cart items
    cart_items = db.query(CartItem).filter(
        CartItem.id.in_(cart_item_ids), CartItem.user_id == user.id
    ).all()
    if len(cart_items) != len(cart_item_ids):
        raise OrderCreationError("购物车项不存在")
    if not cart_items:
        raise OrderCreationError("请选择要结算的商品")

    # Check stock and calculate total
    total_amount = 0
    order_items_data = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or not product.is_active:
            raise OrderCreationError(f"商品「{item.product.name}」已下架")
        if item.quantity > product.stock:
            raise OrderCreationError(f"商品「{product.name}」库存不足，当前库存: {product.stock}")

        # Deduct stock atomically
        result = (
            db.query(Product)
            .filter(Product.id == product.id, Product.stock >= item.quantity)
            .update({"stock": Product.stock - item.quantity})
        )
        if result == 0:
            raise OrderCreationError(f"商品「{product.name}」库存不足")

        order_items_data.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "price_at_time": product.price,
        })
        total_amount += product.price * item.quantity

    # Create order
    order = Order(
        user_id=user.id,
        order_no=generate_order_no(),
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        address_snapshot={
            "receiver_name": address.receiver_name,
            "phone": address.phone,
            "province": address.province,
            "city": address.city,
            "district": address.district,
            "detail": address.detail,
        },
    )
    db.add(order)
    db.flush()

    # Create order items
    for item_data in order_items_data:
        db.add(OrderItem(order_id=order.id, **item_data))

    # Delete cart items
    db.query(CartItem).filter(CartItem.id.in_(cart_item_ids)).delete(synchronize_session=False)

    db.commit()
    db.refresh(order)
    return order
