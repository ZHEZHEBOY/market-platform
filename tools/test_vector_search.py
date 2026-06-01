# -*- coding: utf-8 -*-
"""测试向量搜索模块"""
import sys
import os
from pathlib import Path

# HuggingFace 镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

def test_chromadb():
    """测试 ChromaDB 连接"""
    print("1. 测试 ChromaDB...")
    import chromadb
    client = chromadb.Client()
    collection = client.create_collection("test")
    collection.add(
        ids=["1"],
        documents=["test document"],
        embeddings=[[0.1, 0.2, 0.3]],
    )
    assert collection.count() == 1
    print("   ✅ ChromaDB 正常")

def test_sentence_transformers():
    """测试 sentence-transformers"""
    print("2. 测试 sentence-transformers...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    embeddings = model.encode(["测试文本"])
    assert embeddings.shape[0] == 1
    assert embeddings.shape[1] > 0
    print(f"   ✅ 模型加载成功, 向量维度: {embeddings.shape[1]}")

def test_chinese_search():
    """测试中文语义搜索"""
    print("3. 测试中文语义搜索...")
    from sentence_transformers import SentenceTransformer
    import numpy as np

    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

    documents = [
        "iPhone 16 Pro 苹果手机",
        "小米14 Ultra 安卓手机",
        "MacBook Pro 笔记本电脑",
        "AirPods Pro 无线耳机",
        "Nike 运动鞋 跑步鞋",
    ]

    query = "适合跑步的鞋子"

    doc_embeddings = model.encode(documents, normalize_embeddings=True)
    query_embedding = model.encode([query], normalize_embeddings=True)

    # 余弦相似度
    scores = np.dot(doc_embeddings, query_embedding.T).flatten()
    ranked = sorted(zip(documents, scores), key=lambda x: -x[1])

    print(f"   查询: '{query}'")
    for doc, score in ranked[:3]:
        print(f"   {score:.4f} - {doc}")

    assert ranked[0][0] == "Nike 运动鞋 跑步鞋"
    print("   ✅ 语义搜索正确")

if __name__ == "__main__":
    print("=" * 50)
    print("向量搜索模块测试")
    print("=" * 50)

    try:
        test_chromadb()
    except Exception as e:
        print(f"   ❌ ChromaDB 测试失败: {e}")

    try:
        test_sentence_transformers()
    except Exception as e:
        print(f"   ❌ sentence-transformers 测试失败: {e}")

    try:
        test_chinese_search()
    except Exception as e:
        print(f"   ❌ 中文搜索测试失败: {e}")

    print("\n测试完成!")
