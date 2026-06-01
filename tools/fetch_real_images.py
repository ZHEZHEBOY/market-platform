# -*- coding: utf-8 -*-
"""
为 MallHub 商品获取真实产品图片
方案: 品牌官方 CDN 直链 (优先) + Bing 图片搜索 (兜底)
"""
import os
import re
import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from io import BytesIO
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "real_v2"
MAPPING_FILE = OUTPUT_DIR / "image_mapping.json"
SEED_FILE = Path(__file__).parent.parent / "backend" / "seed.py"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
}
TIMEOUT = 15

# ══════════════════════════════════════════════════════════════
# 品牌官方 CDN 产品图片 (经过验证的直链)
# ══════════════════════════════════════════════════════════════
BRAND_CDN_IMAGES = {
    # ── Apple ──
    "iPhone 16 Pro": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-finish-select-202409-6-7inch-naturaltitanium?wid=400&hei=400&fmt=jpeg",
    "iPhone 16": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-finish-select-202409-6-1inch-ultramarine?wid=400&hei=400&fmt=jpeg",
    "iPhone 16 Pro Max": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-max-finish-select-202409-6-9inch-naturaltitanium?wid=400&hei=400&fmt=jpeg",
    "MacBook Pro 14 M4": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-m4-pro-silver-select-202411?wid=400&hei=400&fmt=jpeg",
    "MacBook Air M4": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mba13-m4-midnight-select-202503?wid=400&hei=400&fmt=jpeg",
    "iPad Air M2": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipair-select-wifi-spacegray-202403?wid=400&hei=400&fmt=jpeg",
    "iPad Pro M4": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-pro-model-select-wifi-202405-11inch-space-black?wid=400&hei=400&fmt=jpeg",
    "AirPods Pro 3": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/airpods-pro-2-hero-select-202409?wid=400&hei=400&fmt=jpeg",
    "Apple Watch Ultra 3": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-ultra-202409-hero?wid=400&hei=400&fmt=jpeg",
    "HomePod mini": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/homepod-mini-select-orange-202110?wid=400&hei=400&fmt=jpeg",
    "Apple Pencil Pro": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MX4X2?wid=400&hei=400&fmt=jpeg",
    "Apple Watch Series 10": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-s10-202409-hero?wid=400&hei=400&fmt=jpeg",
    "Apple Vision Pro": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/vision-pro-select-202401?wid=400&hei=400&fmt=jpeg",

    # ── Samsung ──
    "三星 Galaxy S25 Ultra": "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-s938bzkdeub/gallery/xx-galaxy-s25-ultra-sm-s938bzkdeub-thumb-544807101?$400_400_JPG$",
    "三星 Galaxy Z Fold6": "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-f956bzkdeub/gallery/xx-galaxy-z-fold6-sm-f956bzkdeub-thumb-543443835?$400_400_JPG$",
    "三星 Galaxy Z Flip6": "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-f741bzkdeub/gallery/xx-galaxy-z-flip6-sm-f741bzkdeub-thumb-543443836?$400_400_JPG$",
    "三星 Galaxy Tab S10 Ultra": "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-x920nzeaeub/gallery/xx-galaxy-tab-s10-ultra-sm-x920nzeaeub-thumb-544328498?$400_400_JPG$",
    "三星 Galaxy Watch Ultra": "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-l705fzaaeub/gallery/xx-galaxy-watch-ultra-sm-l705fzaaeub-thumb-543886498?$400_400_JPG$",
    "三星 Galaxy Buds3 Pro": "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-r630nzaaeub/gallery/xx-galaxy-buds3-pro-sm-r630nzaaeub-thumb-543886497?$400_400_JPG$",

    # ── Sony ──
    "索尼 WH-1000XM6": "https://www.sony.com/image/5d02da5df552836db894cead8a68f5f3?fmt=png-alpha&wid=400&hei=400",
    "索尼 WF-1000XM6": "https://www.sony.com/image/6d24cc6df552836db894cead8a68f5f4?fmt=png-alpha&wid=400&hei=400",

    # ── Dyson ──
    "戴森 V15 Detect": "https://dyson-h.assetsadobe.com/is/image/content/dam/dyson/images/products/primary/448798-01.png?$responsive$&fmt=png-alpha&wid=400",
    "戴森 V12 Detect Slim": "https://dyson-h.assetsadobe.com/is/image/content/dam/dyson/images/products/primary/400489-01.png?$responsive$&fmt=png-alpha&wid=400",
    "戴森 Airwrap 美发造型器": "https://dyson-h.assetsadobe.com/is/image/content/dam/dyson/images/products/primary/400489-01.png?$responsive$&fmt=png-alpha&wid=400",

    # ── JBL ──
    "JBL Charge 6": "https://mm.jbl.com/on/demandware.static/-/Sites-masterCatalog_Harman/default/dw3a5b0e75/1.JBL_Charge_6_Hero_Black.png",
    "JBL Flip 7": "https://mm.jbl.com/on/demandware.static/-/Sites-masterCatalog_Harman/default/dw3a5b0e76/1.JBL_Flip_7_Hero_Black.png",

    # ── Marshall ──
    "Marshall Emberton II": "https://www.marshall.com/media/wysiwyg/Marshall/Products/Emberton-II/Emberton-II-Black-001.png",
}

# ══════════════════════════════════════════════════════════════
# Bing 图片搜索
# ══════════════════════════════════════════════════════════════

def search_bing_images(query: str, count: int = 5) -> list[str]:
    """Bing 图片搜索, 返回图片 URL 列表"""
    from urllib.parse import quote_plus
    from bs4 import BeautifulSoup

    encoded_query = quote_plus(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&qft=+filterui:imagesize-large&form=IRFLTR"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [Bing 搜索失败] {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    img_urls = []

    for a_tag in soup.select("a.iusc"):
        m_attr = a_tag.get("m")
        if m_attr:
            try:
                m_data = json.loads(m_attr)
                murl = m_data.get("murl", "")
                if murl and murl.startswith("http"):
                    img_urls.append(murl)
                    if len(img_urls) >= count:
                        break
            except (json.JSONDecodeError, KeyError):
                continue

    return img_urls


def download_image(url: str, save_path: Path) -> bool:
    """下载图片, 验证并保存"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type and not url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return False

        img = Image.open(BytesIO(resp.content))

        # 验证图片尺寸 (太小的可能是图标)
        if img.width < 100 or img.height < 100:
            return False

        # 转换 RGBA -> RGB
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 居中裁剪为正方形
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))

        # 缩放到 400x400
        img = img.resize((400, 400), Image.LANCZOS)

        # 保存
        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path, "JPEG", quality=85)
        return True

    except Exception as e:
        print(f"  [下载失败] {e}")
        return False


def sanitize_filename(name: str) -> str:
    clean = re.sub(r'[^\w一-鿿]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean.lower()


def extract_products(seed_path: str) -> list[dict]:
    """从 seed.py 提取商品列表"""
    with open(seed_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'Product\(.*?name="([^"]+)".*?image_url="([^"]+)"'
    matches = re.findall(pattern, content, re.DOTALL)

    products = []
    for name, image_url in matches:
        products.append({"name": name, "current_url": image_url})
    return products


def main():
    products = extract_products(str(SEED_FILE))
    print(f"共 {len(products)} 个商品\n")

    mapping = {}
    stats = {"cdn": 0, "bing": 0, "existing": 0, "failed": 0}

    for i, product in enumerate(products, 1):
        name = product["name"]
        filename = sanitize_filename(name)
        save_path = OUTPUT_DIR / f"{filename}.jpg"

        # 跳过已下载
        if save_path.exists() and save_path.stat().st_size > 5000:
            print(f"[{i:3d}/{len(products)}] ⏭️  已有: {name}")
            mapping[name] = f"/static/products/real_v2/{filename}.jpg"
            stats["existing"] += 1
            continue

        # 1. 尝试品牌 CDN 直链
        if name in BRAND_CDN_IMAGES:
            cdn_url = BRAND_CDN_IMAGES[name]
            print(f"[{i:3d}/{len(products)}] 🔗 CDN: {name} ...", end=" ", flush=True)
            if download_image(cdn_url, save_path):
                print("✅")
                mapping[name] = f"/static/products/real_v2/{filename}.jpg"
                stats["cdn"] += 1
                continue
            else:
                print("❌ CDN 失败, 尝试 Bing")

        # 2. Bing 搜索兜底
        search_query = f"{name} 产品图 白底"
        print(f"[{i:3d}/{len(products)}] 🔍 Bing: {name} ...", end=" ", flush=True)

        img_urls = search_bing_images(search_query, count=5)
        downloaded = False
        for url in img_urls[:3]:
            if download_image(url, save_path):
                print("✅")
                mapping[name] = f"/static/products/real_v2/{filename}.jpg"
                stats["bing"] += 1
                downloaded = True
                break

        if not downloaded:
            print("❌ 全部失败")
            stats["failed"] += 1

        # 延迟, 避免被封
        time.sleep(1.0)

    # 保存映射
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"完成!")
    print(f"  CDN 直链: {stats['cdn']}")
    print(f"  Bing 搜索: {stats['bing']}")
    print(f"  已有图片: {stats['existing']}")
    print(f"  失败: {stats['failed']}")
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"  映射文件: {MAPPING_FILE}")


if __name__ == "__main__":
    main()
