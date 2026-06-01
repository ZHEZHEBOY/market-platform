# -*- coding: utf-8 -*-
"""
Embedding 模型管理
- 文本: BAAI/bge-small-zh-v1.5 (中文语义)
- 图片: openai/clip-vit-base-patch32 (多模态)
"""
import os
import logging
from functools import lru_cache

import torch
import numpy as np

logger = logging.getLogger(__name__)

# HuggingFace 镜像 (国内加速)
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# 检测设备 (优先 CUDA)
if torch.cuda.is_available():
    DEVICE = "cuda"
    gpu_name = torch.cuda.get_device_name(0)
    gpu_mem = torch.cuda.get_device_properties(0).total_mem / 1024**3
    logger.info(f"🚀 GPU 加速: {gpu_name} ({gpu_mem:.1f}GB)")
else:
    DEVICE = "cpu"
    logger.info("⚠️ 使用 CPU (未检测到 CUDA)")


@lru_cache(maxsize=1)
def get_text_model():
    """加载文本 Embedding 模型 (BGE-base-zh)"""
    from sentence_transformers import SentenceTransformer

    model_name = "BAAI/bge-base-zh-v1.5"
    logger.info(f"加载文本模型: {model_name} -> {DEVICE}")
    model = SentenceTransformer(model_name, device=DEVICE)
    # GPU 半精度推理，节省显存
    if DEVICE == "cuda":
        model.half()
        logger.info("启用 FP16 半精度推理")
    logger.info("文本模型加载完成")
    return model


@lru_cache(maxsize=1)
def get_clip_model():
    """加载 CLIP 多模态模型"""
    from transformers import CLIPModel, CLIPProcessor

    model_name = "openai/clip-vit-base-patch32"
    logger.info(f"加载 CLIP 模型: {model_name} -> {DEVICE}")
    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name).to(DEVICE)
    if DEVICE == "cuda":
        model.half()
        logger.info("CLIP 启用 FP16 半精度推理")
    model.eval()
    logger.info("CLIP 模型加载完成")
    return model, processor


def encode_texts(texts: list[str]) -> np.ndarray:
    """批量编码文本为向量

    Args:
        texts: 文本列表

    Returns:
        numpy 数组, shape=(len(texts), 768)
    """
    model = get_text_model()
    batch_size = 256 if DEVICE == "cuda" else 64  # GPU 用更大 batch
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 50,
        batch_size=batch_size,
    )
    return embeddings.astype(np.float32)


def encode_single_text(text: str) -> list[float]:
    """编码单条文本, 返回 list (方便存入 ChromaDB)"""
    vec = encode_texts([text])[0]
    return vec.tolist()


def encode_images(images: list) -> np.ndarray:
    """批量编码图片为向量

    Args:
        images: PIL Image 列表

    Returns:
        numpy 数组, shape=(len(images), 512)
    """
    model, processor = get_clip_model()
    inputs = processor(images=images, return_tensors="pt", padding=True).to(DEVICE)

    with torch.no_grad():
        output = model.get_image_features(**inputs)

    # 兼容不同版本 transformers 的输出格式
    if hasattr(output, 'last_hidden_state'):
        features = output.last_hidden_state[:, 0, :]  # 取 CLS token
    elif isinstance(output, torch.Tensor):
        features = output
    else:
        features = output.pooler_output if hasattr(output, 'pooler_output') else output[0][:, 0, :]

    # L2 归一化
    features = features / features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy().astype(np.float32)


def encode_single_image(image) -> list[float]:
    """编码单张图片, 返回 list"""
    vec = encode_images([image])[0]
    return vec.tolist()


def encode_text_for_clip(text: str) -> list[float]:
    """用 CLIP 编码文本 (用于跨模态检索: 文本搜图片)"""
    model, processor = get_clip_model()
    inputs = processor(text=[text], return_tensors="pt", padding=True).to(DEVICE)

    with torch.no_grad():
        output = model.get_text_features(**inputs)

    if hasattr(output, 'last_hidden_state'):
        features = output.last_hidden_state[:, 0, :]
    elif isinstance(output, torch.Tensor):
        features = output
    else:
        features = output.pooler_output if hasattr(output, 'pooler_output') else output[0][:, 0, :]

    features = features / features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy()[0].astype(np.float32).tolist()
