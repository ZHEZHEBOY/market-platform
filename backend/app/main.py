from contextlib import asynccontextmanager
from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR
from app.middleware import RateLimitMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware
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
from app.routers.notifications import router as notifications_router
from app.routers.images import router as images_router
from app.routers.vector_search import router as vector_search_router

# 配置日志
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="MallHub API",
    version="0.4.0",
    description="MallHub 电商平台 API",
    lifespan=lifespan,
)

# 安全中间件
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(RequestLoggingMiddleware)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
app.include_router(notifications_router)
app.include_router(images_router)
app.include_router(vector_search_router)

uploads_path = Path(UPLOAD_DIR)
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# 静态文件目录（详情图等）
import os
backend_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
static_path = backend_dir / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")
    logging.info(f"Static files served from: {static_path}")
else:
    logging.warning(f"Static directory not found: {static_path}")

# 图片服务端点
from fastapi.responses import FileResponse

@app.get("/api/images/product/{filename}")
async def get_product_image(filename: str):
    """获取商品图片."""
    # 安全检查
    allowed_ext = ('.jpg', '.jpeg', '.png', '.svg', '.webp')
    if not any(filename.lower().endswith(ext) for ext in allowed_ext):
        raise HTTPException(status_code=400, detail="Invalid image format")

    # 在多个目录中查找图片
    search_dirs = [
        backend_dir / "static" / "products" / "real",
        backend_dir / "static" / "products" / "final",
        backend_dir / "static" / "products" / "crawled",
        backend_dir / "static" / "products",
    ]

    for images_dir in search_dirs:
        filepath = images_dir / filename
        if filepath.exists():
            media_type = "image/svg+xml" if filename.endswith('.svg') else "image/jpeg"
            return FileResponse(filepath, media_type=media_type)

    raise HTTPException(status_code=404, detail="Image not found")
