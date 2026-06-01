# -*- coding: utf-8 -*-
"""图片服务 API."""
import os
import hashlib
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["图片服务"])

# 图片目录 - 使用绝对路径
BACKEND_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
IMAGES_DIR = BACKEND_DIR / "static" / "products" / "real"


@router.get("/api/images/product/{filename}")
async def get_product_image(filename: str):
    """获取商品图片."""
    # 安全检查
    if not filename.endswith('.jpg') and not filename.endswith('.png'):
        raise HTTPException(status_code=400, detail="Invalid image format")

    # 检查文件是否存在
    filepath = IMAGES_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(filepath, media_type="image/jpeg")


@router.get("/api/images/product-by-name/{product_name}")
async def get_product_image_by_name(product_name: str):
    """根据商品名获取图片."""
    # 生成安全的文件名
    safe = ""
    for c in product_name:
        if c.isascii() and (c.isalnum() or c in " _-"):
            safe += c
    safe = safe.replace(" ", "_").lower()
    if not safe:
        safe = hashlib.md5(product_name.encode()).hexdigest()[:12]
    filename = f"{safe}.jpg"

    # 检查文件是否存在
    filepath = IMAGES_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(filepath, media_type="image/jpeg")
