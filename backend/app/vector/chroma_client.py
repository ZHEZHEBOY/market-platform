# -*- coding: utf-8 -*-
"""
ChromaDB 客户端管理
- 语义搜索 collection: products_text
- 图片搜索 collection: products_image
- 用户行为 collection: user_behaviors
"""
import logging
from pathlib import Path

import chromadb

logger = logging.getLogger(__name__)

# ChromaDB 持久化目录
CHROMA_DIR = Path(__file__).parent.parent.parent / "data" / "chroma"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Collection 名称
COLLECTION_TEXT = "products_text"     # 文本语义搜索
COLLECTION_IMAGE = "products_image"   # 以图搜图
COLLECTION_BEHAVIOR = "user_behaviors"  # 用户行为 (用于推荐)

_client: chromadb.ClientAPI | None = None


def get_client() -> chromadb.ClientAPI:
    """获取 ChromaDB 持久化客户端 (单例)"""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        logger.info(f"ChromaDB 初始化完成, 目录: {CHROMA_DIR}")
    return _client


def get_text_collection() -> chromadb.Collection:
    """获取商品文本向量 collection"""
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_TEXT,
        metadata={"hnsw:space": "cosine"},  # 余弦相似度
    )


def get_image_collection() -> chromadb.Collection:
    """获取商品图片向量 collection"""
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_IMAGE,
        metadata={"hnsw:space": "cosine"},
    )


def get_behavior_collection() -> chromadb.Collection:
    """获取用户行为 collection"""
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_BEHAVIOR,
        metadata={"hnsw:space": "cosine"},
    )


def reset_all():
    """重置所有 collection (用于重新索引)"""
    client = get_client()
    for name in [COLLECTION_TEXT, COLLECTION_IMAGE, COLLECTION_BEHAVIOR]:
        try:
            client.delete_collection(name)
            logger.info(f"已删除 collection: {name}")
        except Exception:
            pass  # collection 不存在时忽略
    logger.info("所有 collection 已重置")
