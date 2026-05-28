from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR
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
from app.routers.coupons import router as coupons_router
from app.routers.refunds import router as refunds_router
from app.routers.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(title="Market Platform API", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(addresses_router)
app.include_router(orders_router)
app.include_router(payment_router)
app.include_router(admin_router)
app.include_router(seller_router)
app.include_router(reviews_router)
app.include_router(favorites_router)
app.include_router(categories_router)
app.include_router(coupons_router)
app.include_router(refunds_router)
app.include_router(analytics_router)

uploads_path = Path(UPLOAD_DIR)
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")
