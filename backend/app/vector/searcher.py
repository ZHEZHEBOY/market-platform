# -*- coding: utf-8 -*-
"""
向量搜索服务
- 语义搜索: 自然语言 → 文本向量检索
- 以图搜图: 图片 → CLIP 向量检索
- 推荐系统: 用户行为 → 向量聚合 → 检索
"""
import logging
from dataclasses import dataclass

from app.vector.embeddings import encode_single_text, encode_single_image, encode_text_for_clip
from app.vector.chroma_client import (
    get_text_collection,
    get_image_collection,
    get_behavior_collection,
)
from app.vector.synonyms import expand_query, get_category_hint

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果"""
    product_id: int
    name: str
    category: str
    price: int
    image_url: str
    score: float  # 相似度分数 (0~1, 越大越相似)


# ── 季节冲突过滤规则 ──
_SEASONAL_CONFLICTS = {
    "夏天": ["羽绒服", "棉袄", "棉衣", "毛衣", "羊毛", "加绒", "加厚", "保暖", "冬季", "冬装", "雪地靴", "棉靴", "暖手宝", "暖风机", "电暖器"],
    "夏季": ["羽绒服", "棉袄", "棉衣", "毛衣", "羊毛", "加绒", "加厚", "保暖", "冬季", "冬装", "雪地靴", "棉靴"],
    "冬天": ["短袖", "背心", "短裤", "凉鞋", "拖鞋", "防晒", "遮阳", "冰袖", "凉席", "风扇", "空调扇"],
    "冬季": ["短袖", "背心", "短裤", "凉鞋", "拖鞋", "防晒", "遮阳", "冰袖", "凉席", "风扇"],
    "春秋": ["羽绒服", "棉袄", "加绒", "加厚", "短袖", "背心", "凉鞋"],
}


def _filter_seasonal_mismatch(query: str, results: list[SearchResult]) -> list[SearchResult]:
    """过滤季节不匹配的商品"""
    query_lower = query.lower()

    blocked_keywords = []
    for season, keywords in _SEASONAL_CONFLICTS.items():
        if season in query_lower:
            blocked_keywords.extend(keywords)
            break

    if not blocked_keywords:
        return results

    filtered = []
    for r in results:
        name_lower = r.name.lower()
        if any(kw in name_lower for kw in blocked_keywords):
            continue
        filtered.append(r)

    return filtered


def semantic_search(query: str, top_k: int = 20, category: str = None) -> list[SearchResult]:
    """语义搜索 (带同义词扩展)

    Args:
        query: 用户输入的自然语言, 如 "适合跑步的耳机"
        top_k: 返回数量
        category: 可选, 按分类过滤

    Returns:
        按相似度排序的搜索结果
    """
    if not query.strip():
        return []

    collection = get_text_collection()

    # 同义词扩展
    expanded_queries = expand_query(query)
    # 自动推断分类
    if not category:
        category = get_category_hint(query)

    # 收集所有结果 (去重)
    seen_ids = set()
    all_results = []

    for q in expanded_queries[:3]:  # 最多3个扩展查询
        query_embedding = encode_single_text(q)

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, collection.count()),
        }
        if category:
            kwargs["where"] = {"category": category}

        results = collection.query(**kwargs)

        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)

                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 - distance / 2

                all_results.append(SearchResult(
                    product_id=int(doc_id),
                    name=metadata.get("name", ""),
                    category=metadata.get("category", ""),
                    price=metadata.get("price", 0),
                    image_url=metadata.get("image_url", ""),
                    score=round(score, 4),
                ))

    # 按分数排序
    all_results.sort(key=lambda r: r.score, reverse=True)
    search_results = all_results[:top_k]

    # 季节冲突过滤
    search_results = _filter_seasonal_mismatch(query, search_results)

    logger.info(f"语义搜索 '{query}' -> {len(search_results)} 条结果")
    return search_results


def image_search(image, top_k: int = 20) -> list[SearchResult]:
    """以图搜图

    Args:
        image: PIL Image 对象
        top_k: 返回数量

    Returns:
        按视觉相似度排序的搜索结果
    """
    query_embedding = encode_single_image(image)

    collection = get_image_collection()
    if collection.count() == 0:
        logger.warning("图片索引为空, 无法搜索")
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    search_results = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i] if results["distances"] else 0
            score = 1 - distance / 2

            search_results.append(SearchResult(
                product_id=metadata.get("product_id", 0),
                name=metadata.get("name", ""),
                category="",
                price=0,
                image_url=metadata.get("image_path", ""),
                score=round(score, 4),
            ))

    logger.info(f"以图搜图 -> {len(search_results)} 条结果")
    return search_results


def text_search_image(query: str, top_k: int = 20) -> list[SearchResult]:
    """用文本搜索图片 (跨模态检索)

    Args:
        query: 文本描述, 如 "红色运动鞋"
        top_k: 返回数量

    Returns:
        按跨模态相似度排序的结果
    """
    query_embedding = encode_text_for_clip(query)

    collection = get_image_collection()
    if collection.count() == 0:
        logger.warning("图片索引为空, 无法搜索")
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    search_results = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i] if results["distances"] else 0
            score = 1 - distance / 2

            search_results.append(SearchResult(
                product_id=metadata.get("product_id", 0),
                name=metadata.get("name", ""),
                category="",
                price=0,
                image_url=metadata.get("image_path", ""),
                score=round(score, 4),
            ))

    logger.info(f"文本搜图片 '{query}' -> {len(search_results)} 条结果")
    return search_results


def record_user_behavior(user_id: int, product_id: int, behavior_type: str):
    """记录用户行为

    Args:
        user_id: 用户 ID
        product_id: 商品 ID
        behavior_type: 行为类型 (view/click/cart/buy/favorite)
    """
    collection = get_behavior_collection()

    text_collection = get_text_collection()
    try:
        product = text_collection.get(ids=[str(product_id)], include=["embeddings"])
        if product and product["embeddings"]:
            product_vec = product["embeddings"][0]

            weights = {"buy": 5, "favorite": 4, "cart": 3, "click": 2, "view": 1}
            weight = weights.get(behavior_type, 1)

            weighted_vec = [v * weight for v in product_vec]

            behavior_id = f"u{user_id}_p{product_id}_{behavior_type}"
            collection.upsert(
                ids=[behavior_id],
                embeddings=[weighted_vec],
                metadatas=[{
                    "user_id": user_id,
                    "product_id": product_id,
                    "behavior_type": behavior_type,
                    "weight": weight,
                }],
            )
            logger.debug(f"记录行为: user={user_id}, product={product_id}, type={behavior_type}")
    except Exception as e:
        logger.warning(f"记录行为失败: {e}")


def get_recommendations(user_id: int, top_k: int = 20) -> list[SearchResult]:
    """基于用户行为的推荐

    Args:
        user_id: 用户 ID
        top_k: 返回数量

    Returns:
        推荐商品列表
    """
    collection = get_behavior_collection()

    user_behaviors = collection.get(
        where={"user_id": user_id},
        include=["embeddings", "metadatas"],
    )

    if not user_behaviors["ids"]:
        logger.info(f"用户 {user_id} 无行为记录, 返回空")
        return []

    embeddings = user_behaviors["embeddings"]
    metadatas = user_behaviors["metadatas"]

    if not embeddings:
        return []

    total_weight = sum(m.get("weight", 1) for m in metadatas)
    user_vec = [0.0] * len(embeddings[0])
    for vec, meta in zip(embeddings, metadatas):
        w = meta.get("weight", 1)
        for i, v in enumerate(vec):
            user_vec[i] += v * w / total_weight

    text_collection = get_text_collection()
    results = text_collection.query(
        query_embeddings=[user_vec],
        n_results=min(top_k + 10, text_collection.count()),
    )

    interacted = {m.get("product_id") for m in metadatas}

    search_results = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            pid = int(doc_id)
            if pid in interacted:
                continue
            if len(search_results) >= top_k:
                break

            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i] if results["distances"] else 0
            score = 1 - distance / 2

            search_results.append(SearchResult(
                product_id=pid,
                name=metadata.get("name", ""),
                category=metadata.get("category", ""),
                price=metadata.get("price", 0),
                image_url=metadata.get("image_url", ""),
                score=round(score, 4),
            ))

    logger.info(f"推荐 user={user_id} -> {len(search_results)} 条结果")
    return search_results
