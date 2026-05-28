# -*- coding: utf-8 -*-
"""简单内存缓存，用于热点数据."""
import time
from functools import wraps
from typing import Any

_cache: dict[str, tuple[Any, float]] = {}


def cache_get(key: str) -> Any | None:
    """获取缓存."""
    if key in _cache:
        value, expire_time = _cache[key]
        if time.time() < expire_time:
            return value
        del _cache[key]
    return None


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """设置缓存，ttl 单位秒，默认 5 分钟."""
    _cache[key] = (value, time.time() + ttl)


def cache_delete(key: str) -> None:
    """删除缓存."""
    _cache.pop(key, None)


def cache_clear() -> None:
    """清空所有缓存."""
    _cache.clear()


def cached(ttl: int = 300, key_prefix: str = ""):
    """缓存装饰器."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存 key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # 尝试获取缓存
            result = cache_get(cache_key)
            if result is not None:
                return result

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
