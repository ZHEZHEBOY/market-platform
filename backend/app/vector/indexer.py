# -*- coding: utf-8 -*-
"""
商品索引服务 — 将所有商品写入 ChromaDB
- 文本索引: 商品名+描述+分类 → BGE 向量
- 图片索引: 商品图片 → CLIP 向量
"""
import logging
import sys
from pathlib import Path

import numpy as np

from app.vector.embeddings import encode_texts, encode_images
from app.vector.chroma_client import (
    get_text_collection,
    get_image_collection,
    reset_all,
)

logger = logging.getLogger(__name__)

# 批次大小 (ChromaDB 单次 upsert 上限)
BATCH_SIZE = 100


def _build_text_for_embedding(name: str, description: str, category: str) -> str:
    """构建用于 Embedding 的文本 (拼接 name + description + category)"""
    parts = [name]
    if category:
        parts.append(category)
    if description:
        parts.append(description)
    return " ".join(parts)


def index_text_products(products: list[dict], show_progress: bool = True):
    """将商品文本写入 ChromaDB

    Args:
        products: [{"id": int, "name": str, "description": str, "category": str,
                     "price": int, "shop_id": int, "image_url": str}, ...]
    """
    if not products:
        logger.warning("没有商品需要索引")
        return

    collection = get_text_collection()

    # 构建文本
    texts = [
        _build_text_for_embedding(p["name"], p.get("description", ""), p.get("category", ""))
        for p in products
    ]

    # 批量编码
    logger.info(f"开始编码 {len(texts)} 条商品文本...")
    embeddings = encode_texts(texts)
    logger.info(f"编码完成, 向量维度: {embeddings.shape}")

    # 批次写入 ChromaDB
    total = len(products)
    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch_ids = [str(products[i]["id"]) for i in range(start, end)]
        batch_embeddings = embeddings[start:end].tolist()
        batch_metadatas = [
            {
                "name": products[i]["name"],
                "category": products[i].get("category", ""),
                "price": products[i].get("price", 0),
                "shop_id": products[i].get("shop_id", 0),
                "image_url": products[i].get("image_url", ""),
            }
            for i in range(start, end)
        ]
        batch_documents = texts[start:end]

        collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            documents=batch_documents,
        )

        if show_progress:
            logger.info(f"  文本索引进度: {end}/{total}")

    logger.info(f"文本索引完成, 共 {total} 条")


def index_image_products(products: list[dict]):
    """将商品图片写入 ChromaDB

    Args:
        products: [{"id": int, "name": str, "image_path": str}, ...]
    """
    from PIL import Image

    if not products:
        logger.warning("没有商品图片需要索引")
        return

    collection = get_image_collection()

    # 过滤有效图片
    valid_products = []
    valid_images = []
    for p in products:
        img_path = Path(p["image_path"])
        if img_path.exists() and img_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            try:
                img = Image.open(img_path).convert("RGB")
                valid_products.append(p)
                valid_images.append(img)
            except Exception as e:
                logger.warning(f"无法打开图片 {img_path}: {e}")

    if not valid_images:
        logger.warning("没有有效图片可索引")
        return

    # 批量编码
    logger.info(f"开始编码 {len(valid_images)} 张商品图片...")
    embeddings = encode_images(valid_images)
    logger.info(f"编码完成, 向量维度: {embeddings.shape}")

    # 写入 ChromaDB
    total = len(valid_products)
    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch_ids = [f"img_{valid_products[i]['id']}" for i in range(start, end)]
        batch_embeddings = embeddings[start:end].tolist()
        batch_metadatas = [
            {
                "name": valid_products[i]["name"],
                "product_id": valid_products[i]["id"],
                "image_path": str(valid_products[i]["image_path"]),
            }
            for i in range(start, end)
        ]

        collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
        )

        logger.info(f"  图片索引进度: {end}/{total}")

    logger.info(f"图片索引完成, 共 {total} 张")


def reindex_all():
    """重建所有索引 (从数据库读取全量商品)"""
    # 延迟导入, 避免循环依赖
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from app.database import SessionLocal
    from app.models.product import Product
    from app.models.user import User, Shop
    from app.models.category import Category
    from app.models.review import Review
    from app.models.favorite import Favorite
    from app.models.coupon import Coupon
    from app.models.notification import Notification

    # 清空旧索引
    reset_all()

    db = SessionLocal()
    try:
        products = db.query(Product).all()
        logger.info(f"从数据库读取 {len(products)} 个商品")

        # 构建商品数据
        text_data = []
        image_data = []
        for p in products:
            text_data.append({
                "id": p.id,
                "name": p.name,
                "description": p.description or "",
                "category": p.category or "",
                "price": p.price,
                "shop_id": p.shop_id,
                "image_url": p.image_url or "",
            })

            # 解析图片路径
            if p.image_url:
                # 处理相对路径: /static/products/real/xxx.jpg → backend/static/...
                if p.image_url.startswith("/static/"):
                    img_path = Path(__file__).parent.parent.parent / p.image_url.lstrip("/")
                elif p.image_url.startswith("http"):
                    img_path = None  # 远程图片跳过
                else:
                    img_path = None

                if img_path and img_path.exists():
                    image_data.append({
                        "id": p.id,
                        "name": p.name,
                        "image_path": str(img_path),
                    })

        # 索引文本
        index_text_products(text_data)

        # 索引图片 (仅本地图片)
        if image_data:
            logger.info(f"找到 {len(image_data)} 张本地图片, 开始索引...")
            index_image_products(image_data)
        else:
            logger.info("没有找到本地图片, 跳过图片索引")

        logger.info("全量索引完成!")

    finally:
        db.close()
