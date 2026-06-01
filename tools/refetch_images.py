# -*- coding: utf-8 -*-
"""
重新获取主要商品图片 — 使用更精确的搜索词
"""
import sys
import re
import json
import time
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "real_v2"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 需要重新获取的商品 (文件名, 精确搜索词)
PRODUCTS_TO_FIX = [
    ("iphone_17_pro.jpg", "iPhone 17 Pro 手机 产品图"),
    ("iphone_17_pro_max.jpg", "iPhone 17 Pro Max 手机 产品图"),
    ("iphone_17.jpg", "iPhone 17 手机 产品图"),
    ("iphone_17_air.jpg", "iPhone 17 Air 手机 产品图"),
    ("macbook_pro_14_m5.jpg", "MacBook Pro M5 笔记本电脑"),
    ("macbook_air_m5.jpg", "MacBook Air M5 笔记本电脑"),
    ("ipad_air_m2.jpg", "iPad Air M2 平板电脑"),
    ("ipad_pro_m4.jpg", "iPad Pro M4 平板电脑"),
    ("apple_watch_ultra_3.jpg", "Apple Watch Ultra 3 智能手表"),
    ("apple_watch_series_11.jpg", "Apple Watch Series 11 智能手表"),
    ("apple_vision_pro.jpg", "Apple Vision Pro VR头显"),
    ("三星_galaxy_s26_ultra.jpg", "Samsung Galaxy S26 Ultra 手机"),
    ("三星_galaxy_z_fold7.jpg", "Samsung Galaxy Z Fold7 折叠手机"),
    ("三星_galaxy_z_flip7.jpg", "Samsung Galaxy Z Flip7 折叠手机"),
    ("索尼_wh_1000xm6.jpg", "Sony WH-1000XM6 头戴式耳机"),
    ("戴森_v15_detect.jpg", "Dyson V15 Detect 吸尘器"),
    ("jbl_charge_6.jpg", "JBL Charge 6 蓝牙音箱"),
    ("小米17_ultra.jpg", "小米17 Ultra 手机 产品图"),
    ("小米17.jpg", "小米17 手机 产品图"),
    ("小米17_pro.jpg", "小米17 Pro 手机 产品图"),
    ("华为_mate_80.jpg", "华为Mate 80 手机 产品图"),
    ("三星_galaxy_s25_ultra.jpg", "Samsung Galaxy S25 Ultra 手机"),
    ("macbook_pro_14_m4.jpg", "MacBook Pro 14 M4 笔记本"),
    ("airpods_pro_3.jpg", "AirPods Pro 3 耳机"),
    ("apple_watch_series_10.jpg", "Apple Watch Series 10"),
]


def search_bing_images(query, count=5):
    """Bing 图片搜索"""
    from urllib.parse import quote_plus

    encoded_query = quote_plus(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&qft=+filterui:imagesize-large&form=IRFLTR"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  搜索失败: {e}")
        return []

    soup = __import__('bs4', fromlist=['BeautifulSoup']).BeautifulSoup(resp.text, "html.parser")
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


def download_image(url, save_path):
    """下载图片并处理"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type and not url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return False

        img = Image.open(BytesIO(resp.content))

        if img.width < 100 or img.height < 100:
            return False

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

        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path, "JPEG", quality=90)
        return True

    except Exception as e:
        return False


def main():
    print(f"重新获取 {len(PRODUCTS_TO_FIX)} 个主要商品图片\n")

    success = 0
    failed = 0

    for filename, search_query in PRODUCTS_TO_FIX:
        save_path = OUTPUT_DIR / filename
        print(f"  {filename}")
        print(f"    搜索: {search_query} ...", end=" ", flush=True)

        # 搜索图片
        img_urls = search_bing_images(search_query, count=5)

        if not img_urls:
            print("❌ 未找到图片")
            failed += 1
            time.sleep(1.5)
            continue

        # 尝试下载
        downloaded = False
        for url in img_urls[:3]:
            if download_image(url, save_path):
                print("✅")
                success += 1
                downloaded = True
                break

        if not downloaded:
            print("❌ 下载失败")
            failed += 1

        time.sleep(1.5)  # 延迟避免被封

    print(f"\n完成! 成功: {success}, 失败: {failed}")


if __name__ == "__main__":
    main()
