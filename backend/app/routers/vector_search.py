# -*- coding: utf-8 -*-
"""
向量搜索 API
- POST /api/vector/semantic     语义搜索
- POST /api/vector/image        以图搜图
- POST /api/vector/text-image   文本搜图片
- POST /api/vector/behavior     记录用户行为
- GET  /api/vector/recommend    推荐商品
- POST /api/vector/reindex      重建索引 (管理)
"""
import io
import time
import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vector", tags=["向量搜索"])

# ── 简单内存缓存 (query → results, TTL=5min) ──
_search_cache: dict[str, tuple[float, list]] = {}
_CACHE_TTL = 300  # 5分钟


def _get_searcher():
    """延迟导入 searcher (避免启动时加载 torch)"""
    from app.vector.searcher import (
        semantic_search,
        image_search,
        text_search_image,
        record_user_behavior,
        get_recommendations,
    )
    return semantic_search, image_search, text_search_image, record_user_behavior, get_recommendations


def _cache_get(key: str):
    """从缓存获取结果"""
    if key in _search_cache:
        ts, data = _search_cache[key]
        if time.time() - ts < _CACHE_TTL:
            return data
        del _search_cache[key]
    return None


def _cache_set(key: str, data):
    """写入缓存"""
    _search_cache[key] = (time.time(), data)
    # 限制缓存大小
    if len(_search_cache) > 500:
        oldest = min(_search_cache, key=lambda k: _search_cache[k][0])
        del _search_cache[oldest]


@router.get("/health")
async def health_check():
    """检查向量搜索服务状态"""
    from app.vector.chroma_client import get_text_collection, get_image_collection

    text_col = get_text_collection()
    image_col = get_image_collection()

    return {
        "status": "ok",
        "text_index_count": text_col.count(),
        "image_index_count": image_col.count(),
        "cache_size": len(_search_cache),
    }


@router.get("/suggest")
async def suggest_api(
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词"),
    limit: int = Query(5, ge=1, le=10),
):
    """搜索建议 — 输入时实时推荐

    返回商品名称列表（前缀匹配 + 包含匹配）
    """
    from app.database import SessionLocal
    from app.models.product import Product
    import sqlalchemy as sa

    db = SessionLocal()
    try:
        # 前缀匹配优先，然后包含匹配
        prefix_results = (
            db.query(Product.name)
            .filter(Product.is_active == True, Product.name.like(f"{q}%"))
            .limit(limit)
            .all()
        )
        suggestions = [r[0] for r in prefix_results]

        # 不足则补充包含匹配
        if len(suggestions) < limit:
            contains_results = (
                db.query(Product.name)
                .filter(
                    Product.is_active == True,
                    Product.name.contains(q),
                    ~Product.name.in_(suggestions),
                )
                .limit(limit - len(suggestions))
                .all()
            )
            suggestions.extend([r[0] for r in contains_results])

        return {"query": q, "suggestions": suggestions[:limit]}
    finally:
        db.close()


@router.post("/semantic")
async def semantic_search_api(
    query: str = Query(..., description="搜索关键词, 支持自然语言"),
    top_k: int = Query(20, ge=1, le=100, description="返回数量"),
    category: str = Query(None, description="按分类过滤"),
):
    """语义搜索 — 用自然语言搜索商品

    示例:
    - "适合跑步的耳机"
    - "高性价比手机"
    - "送女朋友的礼物"
    """
    # 检查缓存
    cache_key = f"semantic:{query}:{top_k}:{category}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    semantic_search, _, _, _, _ = _get_searcher()
    results = semantic_search(query, top_k=top_k, category=category)

    response = {
        "query": query,
        "total": len(results),
        "results": [
            {
                "product_id": r.product_id,
                "name": r.name,
                "category": r.category,
                "price": r.price,
                "image_url": r.image_url,
                "score": r.score,
            }
            for r in results
        ],
    }

    _cache_set(cache_key, response)
    return response


@router.post("/image")
async def image_search_api(
    file: UploadFile = File(..., description="上传图片"),
    top_k: int = Query(20, ge=1, le=100),
):
    """以图搜图 — 上传图片找到视觉相似的商品"""
    from PIL import Image

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法解析图片: {e}")

    _, image_search, _, _, _ = _get_searcher()
    results = image_search(image, top_k=top_k)

    return {
        "total": len(results),
        "results": [
            {
                "product_id": r.product_id,
                "name": r.name,
                "score": r.score,
                "image_url": r.image_url,
            }
            for r in results
        ],
    }


@router.post("/text-image")
async def text_search_image_api(
    query: str = Query(..., description="图片描述"),
    top_k: int = Query(20, ge=1, le=100),
):
    """用文本搜索图片 (跨模态)

    示例:
    - "红色运动鞋"
    - "白色耳机"
    - "黑色笔记本电脑"
    """
    _, _, text_search_image_fn, _, _ = _get_searcher()
    results = text_search_image_fn(query, top_k=top_k)

    return {
        "query": query,
        "total": len(results),
        "results": [
            {
                "product_id": r.product_id,
                "name": r.name,
                "score": r.score,
                "image_url": r.image_url,
            }
            for r in results
        ],
    }


@router.post("/behavior")
async def record_behavior_api(
    product_id: int = Query(..., description="商品 ID"),
    behavior_type: str = Query(..., description="行为类型: view/click/cart/buy/favorite"),
):
    """记录用户行为 (暂时不需要登录)"""
    if behavior_type not in ("view", "click", "cart", "buy", "favorite"):
        raise HTTPException(status_code=400, detail="无效的行为类型")

    _, _, _, record_behavior, _ = _get_searcher()
    record_behavior(1, product_id, behavior_type)  # demo: user_id=1

    return {"message": "行为已记录", "product_id": product_id, "type": behavior_type}


@router.get("/recommend")
async def recommend_api(top_k: int = Query(20, ge=1, le=100)):
    """获取个性化推荐 (简化版, 不需要登录)"""
    _, _, _, _, get_recommendations_fn = _get_searcher()
    results = get_recommendations_fn(1, top_k=top_k)

    return {
        "total": len(results),
        "results": [
            {
                "product_id": r.product_id,
                "name": r.name,
                "category": r.category,
                "price": r.price,
                "image_url": r.image_url,
                "score": r.score,
            }
            for r in results
        ],
    }


@router.post("/reindex")
async def reindex_api():
    """重建全量索引 (管理接口)"""
    from app.vector.indexer import reindex_all

    # 清空缓存
    _search_cache.clear()

    try:
        reindex_all()
        from app.vector.chroma_client import get_text_collection, get_image_collection
        text_count = get_text_collection().count()
        image_count = get_image_collection().count()

        return {
            "message": "索引重建完成",
            "text_index_count": text_count,
            "image_index_count": image_count,
        }
    except Exception as e:
        logger.error(f"索引重建失败: {e}")
        raise HTTPException(status_code=500, detail=f"索引重建失败: {e}")
