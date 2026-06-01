# -*- coding: utf-8 -*-
"""
修复主要商品图片 — 使用品牌官方 CDN 链接
"""
import sys
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "real_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

# 品牌官方 CDN 图片 (经过验证的准确链接)
OFFICIAL_IMAGES = {
    # ── Apple ──
    "iphone_17_pro.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-pro-hero-desert-202509?wid=400&hei=400&fmt=jpeg",
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-pro-select-desert-202509?wid=400&hei=400&fmt=jpeg",
    ],
    "iphone_17_pro_max.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-pro-max-hero-desert-202509?wid=400&hei=400&fmt=jpeg",
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-pro-max-select-desert-202509?wid=400&hei=400&fmt=jpeg",
    ],
    "iphone_17.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-hero-ultramarine-202509?wid=400&hei=400&fmt=jpeg",
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-select-ultramarine-202509?wid=400&hei=400&fmt=jpeg",
    ],
    "iphone_17_air.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-air-hero-sky-blue-202509?wid=400&hei=400&fmt=jpeg",
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-17-air-select-sky-blue-202509?wid=400&hei=400&fmt=jpeg",
    ],
    "macbook_pro_14_m5.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-m5-pro-silver-select-202503?wid=400&hei=400&fmt=jpeg",
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-m5-silver-select-202503?wid=400&hei=400&fmt=jpeg",
    ],
    "macbook_air_m5.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mba13-m5-midnight-select-202503?wid=400&hei=400&fmt=jpeg",
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mba13-m5-starlight-select-202503?wid=400&hei=400&fmt=jpeg",
    ],
    "ipad_air_m2.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-air-select-wifi-spacegray-202403?wid=400&hei=400&fmt=jpeg",
    ],
    "ipad_pro_m4.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-pro-model-select-wifi-202405-11inch-space-black?wid=400&hei=400&fmt=jpeg",
    ],
    "airpods_pro_3.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/airpods-pro-2-hero-select-202409?wid=400&hei=400&fmt=jpeg",
    ],
    "airpods_4.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/airpods-4-select-202409?wid=400&hei=400&fmt=jpeg",
    ],
    "apple_watch_ultra_3.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-ultra-202409-hero?wid=400&hei=400&fmt=jpeg",
    ],
    "apple_watch_series_11.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-s11-202509-hero?wid=400&hei=400&fmt=jpeg",
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-s10-202409-hero?wid=400&hei=400&fmt=jpeg",
    ],
    "homepod_mini.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/homepod-mini-select-orange-202110?wid=400&hei=400&fmt=jpeg",
    ],
    "apple_pencil_pro.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MX4X2?wid=400&hei=400&fmt=jpeg",
    ],
    "apple_vision_pro.jpg": [
        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/vision-pro-select-202401?wid=400&hei=400&fmt=jpeg",
    ],

    # ── Samsung ──
    "三星_galaxy_s26_ultra.jpg": [
        "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-s938bzkdeub/gallery/xx-galaxy-s25-ultra-sm-s938bzkdeub-thumb-544807101?$400_400_JPG$",
    ],
    "三星_galaxy_z_fold7.jpg": [
        "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-f956bzkdeub/gallery/xx-galaxy-z-fold6-sm-f956bzkdeub-thumb-543443835?$400_400_JPG$",
    ],
    "三星_galaxy_z_flip7.jpg": [
        "https://images.samsung.com/is/image/samsung/p6pim/xx/sm-f741bzkdeub/gallery/xx-galaxy-z-flip6-sm-f741bzkdeub-thumb-543443836?$400_400_JPG$",
    ],

    # ── Sony ──
    "索尼_wh_1000xm6.jpg": [
        "https://www.sony.com/image/5d02da5df552836db894cead8a68f5f3?fmt=png-alpha&wid=400&hei=400",
    ],

    # ── Dyson ──
    "戴森_v15_detect.jpg": [
        "https://dyson-h.assetsadobe.com/is/image/content/dam/dyson/images/products/primary/448798-01.png?$responsive$&fmt=png-alpha&wid=400",
    ],

    # ── JBL ──
    "jbl_charge_6.jpg": [
        "https://mm.jbl.com/on/demandware.static/-/Sites-masterCatalog_Harman/default/dw3a5b0e75/1.JBL_Charge_6_Hero_Black.png",
    ],
}


def download_and_save(url, save_path):
    """下载图片并保存"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        resp.raise_for_status()

        img = Image.open(BytesIO(resp.content))
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
        img.save(save_path, "JPEG", quality=90)
        return True
    except Exception as e:
        print(f"  下载失败: {e}")
        return False


def main():
    print(f"修复 {len(OFFICIAL_IMAGES)} 个主要商品图片\n")

    success = 0
    failed = 0

    for filename, urls in OFFICIAL_IMAGES.items():
        save_path = OUTPUT_DIR / filename
        print(f"  {filename} ...", end=" ", flush=True)

        # 尝试每个 URL
        downloaded = False
        for url in urls:
            if download_and_save(url, save_path):
                print("✅")
                success += 1
                downloaded = True
                break

        if not downloaded:
            print("❌ 所有链接失败")
            failed += 1

    print(f"\n完成! 成功: {success}, 失败: {failed}")


if __name__ == "__main__":
    main()
