# -*- coding: utf-8 -*-
"""下载真实商品图片."""
import os
import sys
import hashlib
import requests
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "backend" / "static" / "products" / "real"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Unsplash 直接图片 URL（已知可用的图片 ID）
# 这些是 Unsplash 上的真实产品相关图片
UNSPLASH_IMAGES = {
    # 手机
    "iphone": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop",
    "samsung": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&h=400&fit=crop",
    "xiaomi": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&h=400&fit=crop",
    "huawei": "https://images.unsplash.com/photo-1616339502592-5e6d46f43ce4?w=400&h=400&fit=crop",

    # 笔记本
    "macbook": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop",
    "laptop_gaming": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&h=400&fit=crop",
    "thinkpad": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop",

    # 平板
    "ipad": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop",

    # 耳机
    "airpods": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=400&h=400&fit=crop",
    "headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
    "earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=400&h=400&fit=crop",

    # 手表
    "smartwatch": "https://images.unsplash.com/photo-1546868871-af0de0ae72be?w=400&h=400&fit=crop",

    # 音箱
    "speaker": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop",

    # 充电器/充电宝
    "charger": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop",
    "powerbank": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400&h=400&fit=crop",

    # 键盘鼠标
    "keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=400&fit=crop",
    "mouse": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=400&fit=crop",

    # 显示器
    "monitor": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&h=400&fit=crop",

    # 相机
    "webcam": "https://images.unsplash.com/photo-1587825140708-dfaf18c4c02e?w=400&h=400&fit=crop",

    # 运动鞋
    "nike_shoes": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
    "adidas_shoes": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",

    # 服装
    "tshirt": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    "jeans": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",
    "jacket": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&h=400&fit=crop",

    # 包包
    "backpack": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop",

    # 护肤品
    "skincare": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop",
    "lipstick": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400&h=400&fit=crop",
    "perfume": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop",

    # 家电
    "tv": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=400&fit=crop",
    "airconditioner": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&h=400&fit=crop",
    "fridge": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=400&h=400&fit=crop",
    "washer": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=400&h=400&fit=crop",
    "vacuum": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=400&fit=crop",

    # 厨房电器
    "ricecooker": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
    "airfryer": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",

    # 食品
    "food": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop",

    # 书籍
    "book": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=400&fit=crop",

    # 家居
    "lamp": "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=400&h=400&fit=crop",
    "sofa": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop",
    "bedding": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400&h=400&fit=crop",
}

# 商品到图片的映射
PRODUCT_IMAGE_MAP = {
    # Apple
    "iPhone 16 Pro": "iphone",
    "iPhone 16": "iphone",
    "iPhone 16 Plus": "iphone",
    "iPhone 16 Pro Max": "iphone",
    "MacBook Pro 14 M4": "macbook",
    "MacBook Air M4": "macbook",
    "iPad Air M2": "ipad",
    "iPad Pro M4": "ipad",
    "AirPods Pro 3": "airpods",
    "AirPods 4": "airpods",
    "Apple Watch Ultra 3": "smartwatch",
    "Apple Watch Series 10": "smartwatch",
    "HomePod mini": "speaker",
    "Apple Pencil Pro": "charger",
    "MagSafe 充电器": "charger",

    # 小米
    "小米14 Ultra": "xiaomi",
    "小米14": "xiaomi",
    "Redmi K80 Pro": "xiaomi",
    "Redmi Note 14 Pro": "xiaomi",
    "小米手环 9": "smartwatch",
    "小米 Watch S4": "smartwatch",
    "小米平板 7 Pro": "ipad",
    "小米电视 S Pro 75": "tv",
    "小米路由器 BE7000": "charger",
    "小米充电宝 30000mAh": "powerbank",
    "小米蓝牙音箱": "speaker",
    "小米智能门锁 Pro": "charger",
    "小米净水器 1200G": "charger",
    "小米扫地机器人 X20": "vacuum",
    "小米空调 巨省电 1.5匹": "airconditioner",

    # 华为
    "华为 Mate 70": "huawei",
    "华为 Mate 70 Pro": "huawei",
    "华为 Mate X6": "huawei",
    "华为 MatePad Pro 13.2": "ipad",
    "华为 Watch GT5 Pro": "smartwatch",
    "华为 Watch GT5": "smartwatch",
    "华为 FreeBuds Pro 3": "earbuds",
    "华为 MateBook X Pro": "thinkpad",
    "华为路由器 BE3 Pro": "charger",
    "华为超级快充充电器 140W": "charger",
    "华为智能音箱": "speaker",
    "华为体脂秤 WiFi版": "charger",

    # 三星
    "Galaxy S25 Ultra": "samsung",
    "Galaxy S25": "samsung",
    "Galaxy S25+": "samsung",
    "Galaxy Z Fold6": "samsung",
    "Galaxy Z Flip6": "samsung",
    "Galaxy Tab S10+": "ipad",
    "Galaxy Watch7": "smartwatch",
    "Galaxy Watch Ultra": "smartwatch",
    "Galaxy Buds3 Pro": "earbuds",
    "Galaxy Ring": "smartwatch",
    "三星 990 Pro 2TB": "charger",
    "三星 Odyssey G9 49寸": "monitor",
    "三星 T9 4TB 移动固态硬盘": "charger",
    "三星 T7 Shield 2TB 移动固态硬盘": "charger",

    # 其他手机
    "OPPO Find X8": "xiaomi",
    "OPPO Find X8 Pro": "xiaomi",
    "vivo X200 Pro": "xiaomi",
    "一加 13": "xiaomi",
    "荣耀 Magic7 Pro": "huawei",
    "iQOO 13": "xiaomi",
    "realme GT7 Pro": "xiaomi",
    "魅族 21 Pro": "xiaomi",
    "ROG 游戏手机 9": "xiaomi",

    # 笔记本
    "联想 Legion Y9000P": "laptop_gaming",
    "ThinkPad X1 Carbon": "thinkpad",
    "华硕 ROG 幻16": "laptop_gaming",
    "戴尔 XPS 14": "thinkpad",
    "Surface Pro 11": "ipad",
    "机械革命 蛟龙16 Pro": "laptop_gaming",
    "宏碁 暗影骑士·擎": "laptop_gaming",
    "微星 泰坦18 Ultra": "laptop_gaming",

    # 音频
    "索尼 WH-1000XM6": "headphones",
    "索尼 WF-1000XM6": "earbuds",
    "Bose QuietComfort Ultra": "headphones",
    "Marshall Emberton II": "speaker",
    "JBL Charge 6": "speaker",
    "JBL Flip 7": "speaker",
    "铁三角 ATH-M50xBT2": "headphones",
    "森海塞尔 Momentum 4": "headphones",

    # 智能手表
    "佳明 Fenix 8": "smartwatch",
    "佳明 Forerunner 965": "smartwatch",
    "Polar Vantage V3": "smartwatch",

    # 家电
    "格力 1.5匹变频空调": "airconditioner",
    "美的 501L 对开门冰箱": "fridge",
    "海尔 10kg 洗烘一体机": "washer",
    "索尼 75寸 XR电视": "tv",
    "海信 85寸 ULED电视": "tv",
    "TCL 98寸 巨幕电视": "tv",
    "西门子 10kg 洗衣机": "washer",
    "三星 650L 法式多门冰箱": "fridge",

    # 护肤品
    "兰蔻 小黑瓶精华": "skincare",
    "雅诗兰黛 小棕瓶精华": "skincare",
    "SK-II 神仙水": "skincare",
    "资生堂 红腰子精华": "skincare",
    "迪奥 999口红": "lipstick",
    "香奈儿 邂逅香水": "skincare",
    "La Mer 海蓝之谜面霜": "skincare",
    "MAC 子弹头口红": "lipstick",
    "YSL 小金条口红": "lipstick",
    "Tom Ford 黑管口红": "lipstick",

    # 运动
    "Nike Air Zoom Pegasus 42": "nike_shoes",
    "Nike ZoomX Vaporfly NEXT%": "nike_shoes",
    "Adidas Ultraboost Light": "adidas_shoes",
    "Adidas Adizero Adios Pro 3": "adidas_shoes",
    "Asics Gel-Kayano 31": "nike_shoes",
    "Salomon Ultra Glide 2": "nike_shoes",
    "北面 冲锋衣": "jacket",
    "Arc'teryx Beta LT 冲锋衣": "jacket",
    "lululemon Align 瑜伽裤": "tshirt",
    "迪卡侬 速干T恤": "tshirt",

    # 数码配件
    "Anker 140W氮化镓充电器": "charger",
    "Anker 737 充电宝": "powerbank",
    "绿联 12合1 扩展坞": "charger",
    "SanDisk 1TB SD卡": "charger",
    "西部数据 SN850X 2TB": "charger",
    "芝奇 Trident Z5 DDR5 64GB": "charger",
    "罗技 MX Master 3S": "mouse",

    # 显示器
    "戴尔 27寸 4K显示器": "monitor",
    "LG 27寸 OLED显示器": "monitor",
    "ROG 32寸 4K电竞显示器": "monitor",

    # 键盘
    "HHKB Professional HYBRID": "keyboard",
    "罗技 G Pro X 键盘": "keyboard",
    "雷蛇 Huntsman V3 Pro": "keyboard",
    "机械键盘 Cherry MX": "keyboard",

    # 鼠标
    "雷蛇 Viper V3 Pro": "mouse",
    "雷蛇 DeathAdder V3": "mouse",

    # 摄像头
    "罗技 Brio 4K 摄像头": "webcam",
    "罗技 C920s 摄像头": "webcam",
    "雷蛇 Kiyo Pro Ultra 摄像头": "webcam",
    "Elgato Stream Deck": "keyboard",
}


def download_image(url: str, filename: str) -> bool:
    """下载图片."""
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        print(f"  [skip] {filename}")
        return True

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            print(f"  [ok] {filename} ({len(resp.content)} bytes)")
            return True
        else:
            print(f"  [fail] {filename}: status={resp.status_code}")
            return False
    except Exception as e:
        print(f"  [error] {filename}: {e}")
        return False


def get_safe_filename(product_name: str) -> str:
    """生成安全的文件名."""
    # 只保留 ASCII 字符
    safe = ""
    for c in product_name:
        if c.isascii() and (c.isalnum() or c in " _-"):
            safe += c
    safe = safe.replace(" ", "_").lower()
    if not safe:
        safe = hashlib.md5(product_name.encode()).hexdigest()[:12]
    return f"{safe}.jpg"


def main():
    """主函数."""
    print("=" * 60)
    print("Download real product images")
    print("=" * 60)

    success = 0
    fail = 0

    for product_name, image_key in PRODUCT_IMAGE_MAP.items():
        if image_key not in UNSPLASH_IMAGES:
            continue

        url = UNSPLASH_IMAGES[image_key]
        filename = get_safe_filename(product_name)
        print(f"\n[{product_name}] -> {image_key}")

        if download_image(url, filename):
            success += 1
        else:
            fail += 1

    print("\n" + "=" * 60)
    print(f"Done! success: {success}, fail: {fail}")
    print(f"Images saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
