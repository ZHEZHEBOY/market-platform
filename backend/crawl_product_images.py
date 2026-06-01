# -*- coding: utf-8 -*-
"""
Bing 图片搜索爬虫 — 为 MallHub 商品下载真实图片
用法: python crawl_product_images.py [--limit N] [--dry-run]
"""
import os
import re
import sys
import time
import hashlib
import argparse
import requests
from pathlib import Path
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# Windows 终端 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── 配置 ──
SEED_FILE = Path(__file__).parent / "seed.py"
OUTPUT_DIR = Path(__file__).parent / "static" / "products" / "crawled"
IMAGE_SIZE = (400, 400)  # 目标尺寸
REQUEST_DELAY = 1.5  # 请求间隔(秒)，避免被封
MAX_RETRIES = 3
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def extract_products_from_seed(seed_path: str) -> list[dict]:
    """从 seed.py 中提取所有商品名称和当前 image_url"""
    with open(seed_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 Product(name="...", ..., image_url="...")
    pattern = r'Product\(.*?name="([^"]+)".*?image_url="([^"]+)"'
    matches = re.findall(pattern, content, re.DOTALL)

    products = []
    for name, image_url in matches:
        products.append({"name": name, "current_url": image_url})
    return products


def search_bing_images(query: str, count: int = 5) -> list[str]:
    """在 Bing 图片搜索中查找图片，返回图片 URL 列表"""
    encoded_query = quote_plus(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&qft=+filterui:imagesize-large&form=IRFLTR"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [搜索失败] {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    img_urls = []

    # Bing 图片搜索结果中，图片 URL 存放在 <a> 标签的 m 属性(JSON)中
    for a_tag in soup.select("a.iusc"):
        m_attr = a_tag.get("m")
        if m_attr:
            try:
                import json
                m_data = json.loads(m_attr)
                murl = m_data.get("murl", "")
                if murl and murl.startswith("http"):
                    img_urls.append(murl)
                    if len(img_urls) >= count:
                        break
            except (json.JSONDecodeError, KeyError):
                continue

    # 备用方案：从 img 标签提取
    if not img_urls:
        for img in soup.select("img.mimg"):
            src = img.get("src") or img.get("data-src") or ""
            if src.startswith("http") and "bing.com" not in src:
                img_urls.append(src)
                if len(img_urls) >= count:
                    break

    return img_urls


def download_and_resize(url: str, save_path: Path) -> bool:
    """下载图片并调整为标准尺寸"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        resp.raise_for_status()

        # 验证是图片
        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type and not url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return False

        img = Image.open(BytesIO(resp.content))

        # 转换 RGBA -> RGB
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 居中裁剪为正方形
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))

        # 缩放
        img = img.resize(IMAGE_SIZE, Image.LANCZOS)

        # 保存
        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path, "JPEG", quality=85)
        return True

    except Exception as e:
        print(f"  [下载失败] {e}")
        return False


def sanitize_filename(name: str) -> str:
    """将商品名转为安全文件名"""
    # 移除特殊字符，保留中文、英文、数字
    clean = re.sub(r'[^\w一-鿿]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean.lower()


def main():
    parser = argparse.ArgumentParser(description="Bing 图片搜索爬虫 - MallHub 商品图片")
    parser.add_argument("--limit", type=int, default=0, help="限制爬取数量(0=全部)")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将要爬取的商品，不实际下载")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY, help="请求间隔秒数")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="跳过已有图片的商品")
    args = parser.parse_args()

    # 提取商品
    products = extract_products_from_seed(str(SEED_FILE))
    print(f"从 seed.py 中提取到 {len(products)} 个商品\n")

    if args.dry_run:
        for i, p in enumerate(products, 1):
            print(f"  {i:3d}. {p['name']}")
        return

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 跟踪已用文件名，避免冲突
    used_names = {}
    success_count = 0
    fail_count = 0
    skip_count = 0

    # 生成文件名映射(用于后续更新 seed.py)
    name_mapping = {}

    limit = args.limit if args.limit > 0 else len(products)

    for i, product in enumerate(products[:limit], 1):
        name = product["name"]
        filename = sanitize_filename(name)

        # 处理文件名冲突
        if filename in used_names:
            used_names[filename] += 1
            filename = f"{filename}_{used_names[filename]}"
        else:
            used_names[filename] = 0

        save_path = OUTPUT_DIR / f"{filename}.jpg"

        # 跳过已存在
        if args.skip_existing and save_path.exists():
            print(f"[{i}/{limit}] 跳过(已存在): {name}")
            name_mapping[name] = f"/static/products/crawled/{filename}.jpg"
            skip_count += 1
            continue

        print(f"[{i}/{limit}] 搜索: {name} ...", end=" ", flush=True)

        # 搜索图片
        search_query = f"{name} 产品图"
        img_urls = search_bing_images(search_query, count=5)

        if not img_urls:
            print("❌ 未找到图片")
            fail_count += 1
            continue

        # 尝试下载
        downloaded = False
        for url in img_urls[:3]:  # 最多尝试前3个
            if download_and_resize(url, save_path):
                print(f"✅ 已保存: {filename}.jpg")
                name_mapping[name] = f"/static/products/crawled/{filename}.jpg"
                success_count += 1
                downloaded = True
                break

        if not downloaded:
            print("❌ 下载失败")
            fail_count += 1

        # 延迟
        time.sleep(args.delay)

    # 输出统计
    print(f"\n{'='*50}")
    print(f"爬取完成!")
    print(f"  成功: {success_count}")
    print(f"  跳过: {skip_count}")
    print(f"  失败: {fail_count}")
    print(f"  图片保存在: {OUTPUT_DIR}")

    # 保存映射文件(用于更新 seed.py)
    mapping_file = OUTPUT_DIR / "image_mapping.json"
    import json
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(name_mapping, f, ensure_ascii=False, indent=2)
    print(f"  映射文件: {mapping_file}")


if __name__ == "__main__":
    main()
