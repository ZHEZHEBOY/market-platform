from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.cart import router as cart_router
from app.routers.addresses import router as addresses_router
from app.routers.orders import router as orders_router
from app.routers.payment import router as payment_router
from app.routers.admin import router as admin_router
from app.routers.seller import router as seller_router
from app.routers.reviews import router as reviews_router
from app.routers.favorites import router as favorites_router
from app.routers.categories import router as categories_router

__all__ = [
    "auth_router", "products_router", "cart_router", "addresses_router",
    "orders_router", "payment_router", "admin_router", "seller_router",
    "reviews_router", "favorites_router", "categories_router",
]
