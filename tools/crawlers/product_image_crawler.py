# -*- coding: utf-8 -*-
"""
商品图片爬虫脚本
用于从公开资源获取商品图片，扩充商品数据库

使用方法:
    python product_image_crawler.py

功能:
    1. 从 Unsplash 获取高质量产品图片（需要 API key）
    2. 从 Lorem Picsum 获取随机图片作为占位
    3. 生成品牌风格的 SVG 产品图
    4. 批量下载并保存到本地
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "backend" / "static" / "products" / "crawled"
PRODUCTS_JSON = PROJECT_ROOT / "backend" / "data" / "products_extended.json"


class ProductImageCrawler:
    """商品图片爬虫基类"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.downloaded = 0
        self.failed = 0

    def download_image(self, url: str, filename: str) -> Optional[str]:
        """下载图片并保存到本地"""
        try:
            filepath = self.output_dir / filename
            if filepath.exists():
                print(f"  [skip] {filename}")
                return str(filepath)

            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                with open(filepath, 'wb') as f:
                    f.write(data)

            self.downloaded += 1
            print(f"  [ok] {filename} ({len(data)} bytes)")
            return str(filepath)
        except Exception as e:
            self.failed += 1
            # 避免在错误消息中包含中文字符
            error_msg = str(e).encode('ascii', errors='ignore').decode()
            print(f"  [fail] {filename}: {error_msg}")
            return None

    def generate_filename(self, brand: str, product: str, suffix: str = "") -> str:
        """生成标准化的文件名（使用哈希确保ASCII兼容）"""
        # 中文品牌名映射
        brand_map = {
            "小米": "xiaomi", "华为": "huawei", "三星": "samsung",
            "OPPO": "oppo", "vivo": "vivo", "一加": "oneplus",
            "荣耀": "honor", "魅族": "meizu", "努比亚": "nubia",
            "联想": "lenovo", "戴尔": "dell", "华硕": "asus",
            "索尼": "sony", "松下": "panasonic", "飞利浦": "philips",
            "格力": "gree", "美的": "midea", "海尔": "haier",
            "海信": "hisense", "TCL": "tcl", "西门子": "siemens",
            "九阳": "joyoung", "苏泊尔": "supor", "格兰仕": "galanz",
            "戴森": "dyson", "科沃斯": "ecovacs", "石头": "roborock",
            "追觅": "dreame", "兰蔻": "lancome", "雅诗兰黛": "esteelauder",
            "资生堂": "shiseido", "迪奥": "dior", "香奈儿": "chanel",
            "优衣库": "uniqlo", "匡威": "converse", "新秀丽": "samsonite",
            "三只松鼠": "3squirrels", "星巴克": "starbucks",
            "蒙牛": "mengniu", "伊利": "yili", "安慕希": "ambrosial",
            "绿联": "ugreen", "罗技": "logitech", "雷蛇": "razer",
            "明基": "benq", "佳明": "garmin", "北面": "thenorthface",
        }

        # 转换品牌名
        clean_brand = brand_map.get(brand, brand)
        # 清理品牌名
        clean_brand = ''.join(c for c in clean_brand if c.isascii() and (c.isalnum() or c in '_-'))
        clean_brand = clean_brand.lower() or hashlib.md5(brand.encode()).hexdigest()[:8]

        # 清理产品名
        clean_product = ''.join(c for c in product if c.isascii() and (c.isalnum() or c in ' _-'))
        clean_product = clean_product.replace(" ", "_").lower() or hashlib.md5(product.encode()).hexdigest()[:8]

        name = f"{clean_brand}_{clean_product}"
        if suffix:
            name += f"_{suffix}"

        # 最终检查，确保纯 ASCII
        try:
            name.encode('ascii')
        except UnicodeEncodeError:
            name = hashlib.md5(name.encode()).hexdigest()[:16]

        return f"{name}.jpg"


class UnsplashCrawler(ProductImageCrawler):
    """从 Unsplash 获取图片（需要 API key）"""

    BASE_URL = "https://api.unsplash.com"

    def __init__(self, output_dir: Path, api_key: str):
        super().__init__(output_dir)
        self.api_key = api_key

    def search_and_download(self, query: str, brand: str, product: str, count: int = 1):
        """搜索并下载 Unsplash 图片"""
        if not self.api_key:
            print("[跳过] 未配置 Unsplash API key")
            return

        try:
            encoded_query = urllib.parse.quote(query)
            url = f"{self.BASE_URL}/search/photos?query={encoded_query}&per_page={count}&client_id={self.api_key}"

            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                results = data.get("results", [])

            for i, photo in enumerate(results[:count]):
                img_url = photo["urls"]["regular"]  # 1080px width
                filename = self.generate_filename(brand, product, f"unsplash_{i}")
                self.download_image(img_url, filename)
                time.sleep(0.5)  # 限速

        except Exception as e:
            print(f"[错误] Unsplash 搜索失败: {e}")


class PicsumCrawler(ProductImageCrawler):
    """从 Lorem Picsum 获取随机图片"""

    BASE_URL = "https://picsum.photos"

    def download_by_id(self, photo_id: int, brand: str, product: str, width: int = 600, height: int = 600):
        """通过 ID 下载 Picsum 图片"""
        url = f"{self.BASE_URL}/id/{photo_id}/{width}/{height}"
        filename = self.generate_filename(brand, product, f"picsum_{photo_id}")
        return self.download_image(url, filename)

    def download_random(self, brand: str, product: str, seed: str, width: int = 600, height: int = 600):
        """通过种子下载随机但固定的图片"""
        url = f"{self.BASE_URL}/seed/{seed}/{width}/{height}"
        filename = self.generate_filename(brand, product, "picsum")
        # 确保 filename 是纯 ASCII
        try:
            filename.encode('ascii')
        except UnicodeEncodeError:
            filename = hashlib.md5(filename.encode()).hexdigest()[:16] + ".jpg"
        return self.download_image(url, filename)


class SVGGenerator(ProductImageCrawler):
    """生成 SVG 风格的产品图"""

    def generate_product_card(self, brand: str, product_name: str, color: str, price: str, features: list) -> str:
        """生成产品卡片 SVG"""
        feature_tags = ""
        for i, f in enumerate(features[:3]):
            y = 260 + i * 40
            feature_tags += f'<text x="40" y="{y}" font-family="Arial" font-size="14" fill="{color}">• {f}</text>'

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="450" viewBox="0 0 400 450">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff"/>
      <stop offset="100%" style="stop-color:#f8f9fa"/>
    </linearGradient>
  </defs>
  <rect width="400" height="450" fill="url(#bg)" rx="16"/>
  <rect width="400" height="4" fill="{color}" rx="2"/>
  <rect x="40" y="30" width="80" height="30" rx="15" fill="{color}"/>
  <text x="80" y="51" text-anchor="middle" font-family="Arial" font-size="12" fill="white" font-weight="bold">{brand}</text>
  <text x="40" y="110" font-family="Arial" font-size="24" fill="#1a1a1a" font-weight="bold">{product_name}</text>
  <text x="40" y="140" font-family="Arial" font-size="14" fill="#666">官方正品 · 全国联保</text>
  <line x1="40" y1="160" x2="360" y2="160" stroke="#eee" stroke-width="1"/>
  <text x="40" y="200" font-family="Arial" font-size="16" fill="#1a1a1a" font-weight="600">核心卖点</text>
  {feature_tags}
  <text x="40" y="400" font-family="Arial" font-size="28" fill="{color}" font-weight="bold">¥{price}</text>
  <rect x="40" y="420" width="120" height="36" rx="18" fill="{color}"/>
  <text x="100" y="444" text-anchor="middle" font-family="Arial" font-size="14" fill="white">立即购买</text>
</svg>'''
        return svg

    def save_svg(self, svg_content: str, filename: str) -> str:
        """保存 SVG 文件"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"  [生成] {filename}")
        return str(filepath)


# ============================================================
# 商品数据定义
# ============================================================

PRODUCTS_TO_CRAWL = [
    # Apple
    {"brand": "Apple", "product": "iPhone 16 Pro", "query": "iphone 16 pro", "color": "#1A1A1A", "price": "8999",
     "features": ["A18 Pro芯片", "钛金属设计", "4800万像素"]},
    {"brand": "Apple", "product": "MacBook Pro M4", "query": "macbook pro 2024", "color": "#1A1A1A", "price": "14999",
     "features": ["M4 Pro芯片", "Liquid Retina XDR", "18小时续航"]},
    {"brand": "Apple", "product": "iPad Air M2", "query": "ipad air m2", "color": "#1A1A1A", "price": "4799",
     "features": ["M2芯片", "11英寸屏幕", "Apple Pencil Pro"]},
    {"brand": "Apple", "product": "AirPods Pro 3", "query": "airpods pro", "color": "#1A1A1A", "price": "1899",
     "features": ["H3芯片", "自适应降噪", "空间音频"]},
    {"brand": "Apple", "product": "Apple Watch Ultra 3", "query": "apple watch ultra", "color": "#1A1A1A", "price": "6499",
     "features": ["钛金属表壳", "双频GPS", "100米防水"]},

    # 小米
    {"brand": "小米", "product": "小米14 Ultra", "query": "xiaomi 14 ultra", "color": "#FF6900", "price": "5999",
     "features": ["骁龙8 Gen3", "徕卡光学镜头", "2K AMOLED"]},
    {"brand": "小米", "product": "小米14", "query": "xiaomi 14", "color": "#FF6900", "price": "3999",
     "features": ["骁龙8 Gen3", "徕卡光学", "小尺寸旗舰"]},
    {"brand": "小米", "product": "Redmi K80 Pro", "query": "redmi k80", "color": "#FF6900", "price": "3299",
     "features": ["骁龙8至尊版", "2K屏", "6000mAh"]},
    {"brand": "小米", "product": "小米手环 9", "query": "xiaomi band", "color": "#FF6900", "price": "249",
     "features": ["AMOLED屏", "血氧监测", "14天续航"]},

    # 华为
    {"brand": "华为", "product": "Mate 70", "query": "huawei mate 70", "color": "#CF0A2C", "price": "5499",
     "features": ["麒麟9100", "鸿蒙系统", "超光谱影像"]},
    {"brand": "华为", "product": "Mate X6", "query": "huawei mate x6", "color": "#CF0A2C", "price": "12999",
     "features": ["折叠屏", "鸿蒙系统", "XMAGE影像"]},

    # 三星
    {"brand": "三星", "product": "Galaxy S25 Ultra", "query": "samsung galaxy s25", "color": "#1428A0", "price": "9999",
     "features": ["骁龙8 Elite", "2亿像素", "Galaxy AI"]},
    {"brand": "三星", "product": "Galaxy Z Fold6", "query": "samsung fold", "color": "#1428A0", "price": "13999",
     "features": ["折叠屏", "S Pen", "多任务处理"]},

    # 数码配件
    {"brand": "Anker", "product": "140W充电器", "query": "anker charger", "color": "#0AB4E8", "price": "399",
     "features": ["140W大功率", "4口USB-C", "氮化镓技术"]},
    {"brand": "索尼", "product": "WH-1000XM6", "query": "sony headphones", "color": "#1A1A1A", "price": "2499",
     "features": ["V2处理器", "40小时续航", "LDAC Hi-Res"]},
    {"brand": "JBL", "product": "Charge 6", "query": "jbl speaker", "color": "#FF6900", "price": "1299",
     "features": ["蓝牙5.3", "IP67防水", "20小时续航"]},

    # 家电
    {"brand": "戴森", "product": "V15 Detect", "query": "dyson vacuum", "color": "#6B21A8", "price": "4990",
     "features": ["激光探测", "240AW吸力", "60分钟续航"]},
    {"brand": "索尼", "product": "65寸XR电视", "query": "sony tv oled", "color": "#1A1A1A", "price": "12999",
     "features": ["OLED面板", "XR认知芯片", "4K 120Hz"]},

    # 运动
    {"brand": "Nike", "product": "Air Zoom Pegasus 42", "query": "nike running shoes", "color": "#1A1A1A", "price": "899",
     "features": ["React泡棉", "Zoom Air气垫", "飞织鞋面"]},
    {"brand": "Adidas", "product": "Ultraboost Light", "query": "adidas ultraboost", "color": "#1A1A1A", "price": "1099",
     "features": ["Light BOOST", "Continental橡胶", "Primeknit"]},

    # 护肤品
    {"brand": "兰蔻", "product": "小黑瓶精华", "query": "lancome serum", "color": "#1A1A1A", "price": "799",
     "features": ["微生态科技", "7大益生元", "修护肌底"]},
    {"brand": "SK-II", "product": "神仙水", "query": "skii essence", "color": "#E4002B", "price": "1599",
     "features": ["Pitera精华", "90%天然成分", "改善肤质"]},
]


def main():
    """主函数"""
    print("=" * 60)
    print("商品图片爬虫")
    print("=" * 60)

    # 创建输出目录
    svg_dir = OUTPUT_DIR / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)

    # 初始化爬虫
    picsum = PicsumCrawler(OUTPUT_DIR)
    svg_gen = SVGGenerator(svg_dir)

    # 可选: 配置 Unsplash API key
    unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if unsplash_key:
        unsplash = UnsplashCrawler(OUTPUT_DIR, unsplash_key)
        print(f"[配置] Unsplash API key 已设置")
    else:
        unsplash = None
        print("[提示] 未配置 Unsplash API key，将使用其他图片源")

    print(f"\n开始处理 {len(PRODUCTS_TO_CRAWL)} 个商品...")
    print("-" * 60)

    # 用于存储扩展的商品数据
    extended_products = []

    for item in PRODUCTS_TO_CRAWL:
        brand = item["brand"]
        product = item["product"]
        query = item["query"]
        color = item["color"]
        price = item["price"]
        features = item["features"]

        try:
            # 使用安全的打印方式
            safe_brand = brand.encode('ascii', errors='ignore').decode()
            safe_product = product.encode('ascii', errors='ignore').decode()
            print(f"\n[{safe_brand}] {safe_product}")

            # 1. 从 Unsplash 获取图片（如果有 API key）
            if unsplash:
                unsplash.search_and_download(query, brand, product, count=1)

            # 2. 从 Picsum 获取随机图片
            seed = f"{brand}_{product}".replace(" ", "_").lower()
            # 确保 seed 是 ASCII
            try:
                seed.encode('ascii')
            except UnicodeEncodeError:
                seed = hashlib.md5(seed.encode()).hexdigest()[:16]
            picsum.download_random(brand, product, seed)

            # 3. 生成 SVG 产品图
            main_svg = svg_gen.generate_product_card(brand, product, color, price, features)
            # 使用哈希生成安全的文件名
            safe_name = hashlib.md5(f"{brand}_{product}".encode()).hexdigest()[:16]
            svg_filename = f"{safe_name}_main.svg"
            svg_gen.save_svg(main_svg, svg_filename)

            # 记录商品数据
            extended_products.append({
                "brand": brand,
                "name": product,
                "color": color,
                "price": price,
                "features": features,
                "image_seed": seed,
            })
        except Exception as e:
            error_msg = str(e).encode('ascii', errors='ignore').decode()
            print(f"  [error] {error_msg[:50]}")
            continue

    # 保存扩展商品数据
    PRODUCTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(PRODUCTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(extended_products, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"完成! 下载: {picsum.downloaded}, 失败: {picsum.failed}")
    print(f"SVG 生成: {len(PRODUCTS_TO_CRAWL)} 个商品")
    print(f"商品数据已保存到: {PRODUCTS_JSON}")
    print("=" * 60)


if __name__ == "__main__":
    main()
