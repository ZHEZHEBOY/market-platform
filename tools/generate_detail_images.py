# -*- coding: utf-8 -*-
"""
为 MallHub 商品生成精美详情介绍图
风格参考淘宝/京东商品详情页 — 规格参数卡 + 卖点展示 + 品牌配色
"""
import os
import re
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEED_FILE = Path(__file__).parent.parent / "backend" / "seed.py"
OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "details"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 字体 ──
FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",     # 黑体
    "C:/Windows/Fonts/simsun.ttc",     # 宋体
]

def get_font(size):
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()


# ── 品牌配色 ──
BRAND_COLORS = {
    "apple":    ("#1a1a1a", "#f5f5f7"),
    "iphone":   ("#1a1a1a", "#f5f5f7"),
    "macbook":  ("#1a1a1a", "#f5f5f7"),
    "ipad":     ("#1a1a1a", "#f5f5f7"),
    "airpods":  ("#1a1a1a", "#f5f5f7"),
    "小米":     ("#ff6900", "#ffffff"),
    "redmi":    ("#ff6900", "#ffffff"),
    "华为":     ("#cf0a2c", "#ffffff"),
    "huawei":   ("#cf0a2c", "#ffffff"),
    "三星":     ("#1428a0", "#ffffff"),
    "samsung":  ("#1428a0", "#ffffff"),
    "oppo":     ("#1a73e8", "#ffffff"),
    "vivo":     ("#415fff", "#ffffff"),
    "一加":     ("#eb0028", "#ffffff"),
    "荣耀":     ("#0ab4e8", "#ffffff"),
    "索尼":     ("#1a1a1a", "#ffffff"),
    "sony":     ("#1a1a1a", "#ffffff"),
    "戴森":     ("#6b21a8", "#ffffff"),
    "dyson":    ("#6b21a8", "#ffffff"),
    "nike":     ("#1a1a1a", "#ffffff"),
    "adidas":   ("#1a1a1a", "#ffffff"),
    "联想":     ("#e4002b", "#ffffff"),
    "lenovo":   ("#e4002b", "#ffffff"),
    "thinkpad": ("#e4002b", "#ffffff"),
    "戴尔":     ("#007db8", "#ffffff"),
    "dell":     ("#007db8", "#ffffff"),
    "华硕":     ("#ff005a", "#ffffff"),
    "rog":      ("#ff005a", "#ffffff"),
    "罗技":     ("#00b894", "#ffffff"),
    "logitech": ("#00b894", "#ffffff"),
    "雷蛇":     ("#44d62c", "#000000"),
    "razer":    ("#44d62c", "#000000"),
    "飞利浦":   ("#0ab4e8", "#ffffff"),
    "philips":  ("#0ab4e8", "#ffffff"),
    "美的":     ("#00b894", "#ffffff"),
    "九阳":     ("#ff6900", "#ffffff"),
    "松下":     ("#00529b", "#ffffff"),
    "panasonic":("#00529b", "#ffffff"),
    "迪卡侬":   ("#00529b", "#ffffff"),
    "decathlon":("#00529b", "#ffffff"),
    "jbl":      ("#ff6900", "#ffffff"),
    "乐高":     ("#ffd700", "#000000"),
    "lego":     ("#ffd700", "#000000"),
    "ikea":     ("#00529b", "#ffffff"),
    "宜家":     ("#00529b", "#ffffff"),
    "muji":     ("#f5f5dc", "#333333"),
    "无印":     ("#f5f5dc", "#333333"),
    "星巴克":   ("#00704a", "#ffffff"),
    "dior":     ("#e4002b", "#ffffff"),
    "迪奥":     ("#e4002b", "#ffffff"),
    "chanel":   ("#1a1a1a", "#ffffff"),
    "香奈儿":   ("#1a1a1a", "#ffffff"),
    "sk-ii":    ("#e4002b", "#ffffff"),
    "兰蔻":     ("#00529b", "#ffffff"),
    "lancome":  ("#00529b", "#ffffff"),
    "surface":  ("#7c7c7c", "#ffffff"),
    "garmin":   ("#00b894", "#ffffff"),
    "bose":     ("#1a1a1a", "#ffffff"),
    "marshall": ("#1a1a1a", "#ffffff"),
    "lg":       ("#a50034", "#ffffff"),
    "realme":   ("#ffc700", "#000000"),
    "iqoo":     ("#1a73e8", "#ffffff"),
    "魅族":     ("#0ab4e8", "#ffffff"),
    "meizu":    ("#0ab4e8", "#ffffff"),
    "anker":    ("#0ab4e8", "#ffffff"),
    "安克":     ("#0ab4e8", "#ffffff"),
    "科沃斯":   ("#00b894", "#ffffff"),
    "ecovacs":  ("#00b894", "#ffffff"),
    "西门子":   ("#1a1a1a", "#ffffff"),
    "tcl":      ("#e4002b", "#ffffff"),
    "海信":     ("#00529b", "#ffffff"),
    "小米":     ("#ff6900", "#ffffff"),
    "李宁":     ("#e4002b", "#ffffff"),
    "安踏":     ("#e4002b", "#ffffff"),
    "斐乐":     ("#1a1a1a", "#ffffff"),
    "fila":     ("#1a1a1a", "#ffffff"),
    "coach":    ("#8b4513", "#ffffff"),
    "蔻驰":     ("#8b4513", "#ffffff"),
    "珀莱雅":   ("#e4002b", "#ffffff"),
    "薇诺娜":   ("#00b894", "#ffffff"),
    "完美日记": ("#e4002b", "#ffffff"),
    "花西子":   ("#ff6900", "#ffffff"),
    "欧莱雅":   ("#1a1a1a", "#ffffff"),
    "修丽可":   ("#00529b", "#ffffff"),
    "海蓝之谜": ("#00529b", "#ffffff"),
    "阿玛尼":   ("#1a1a1a", "#ffffff"),
    "科颜氏":   ("#00529b", "#ffffff"),
    "北面":     ("#1a1a1a", "#ffffff"),
    "thenorthface": ("#1a1a1a", "#ffffff"),
    "优衣库":   ("#e4002b", "#ffffff"),
    "uniqlo":   ("#e4002b", "#ffffff"),
    "new balance": ("#e4002b", "#ffffff"),
    "匡威":     ("#1a1a1a", "#ffffff"),
    "converse": ("#1a1a1a", "#ffffff"),
    "lululemon":("#1a1a1a", "#ffffff"),
    "三只松鼠": ("#e4002b", "#ffffff"),
    "良品铺子": ("#e4002b", "#ffffff"),
    "元气森林": ("#00b894", "#ffffff"),
    "三顿半":   ("#1a1a1a", "#ffffff"),
    "瑞幸":     ("#00529b", "#ffffff"),
    "农夫山泉": ("#00b894", "#ffffff"),
    "可口可乐": ("#e4002b", "#ffffff"),
    "百事可乐": ("#00529b", "#ffffff"),
    "蒙牛":     ("#00529b", "#ffffff"),
    "伊利":     ("#00529b", "#ffffff"),
    "飞鹤":     ("#00529b", "#ffffff"),
    "费雪":     ("#e4002b", "#ffffff"),
    "好孩子":   ("#0ab4e8", "#ffffff"),
    "贝亲":     ("#ffc0cb", "#333333"),
    "得力":     ("#e4002b", "#ffffff"),
    "晨光":     ("#e4002b", "#ffffff"),
    "蓝月亮":   ("#00529b", "#ffffff"),
    "维达":     ("#00b894", "#ffffff"),
    "水星":     ("#00529b", "#ffffff"),
    "全棉时代": ("#ffc0cb", "#333333"),
    "网易严选": ("#e4002b", "#ffffff"),
    "芙丽芳丝": ("#ffc0cb", "#333333"),
    "敷尔佳":   ("#ffc0cb", "#333333"),
    "安耐晒":   ("#ffd700", "#000000"),
    "太力":     ("#00b894", "#ffffff"),
    "小熊":     ("#ff6900", "#ffffff"),
    "博朗":     ("#1a1a1a", "#ffffff"),
    "摩飞":     ("#ff6900", "#ffffff"),
    "苏泊尔":   ("#00b894", "#ffffff"),
    "格兰仕":   ("#e4002b", "#ffffff"),
    "石头":     ("#1a1a1a", "#ffffff"),
    "追觅":     ("#0ab4e8", "#ffffff"),
    "绿联":     ("#00b894", "#ffffff"),
    "倍思":     ("#1a73e8", "#ffffff"),
    "明基":     ("#00b894", "#ffffff"),
    "benq":     ("#00b894", "#ffffff"),
    "金士顿":   ("#e4002b", "#ffffff"),
    "kingston": ("#e4002b", "#ffffff"),
    "西部数据": ("#00529b", "#ffffff"),
    "芝奇":     ("#e4002b", "#ffffff"),
    "elgato":   ("#1a1a1a", "#ffffff"),
    "佳明":     ("#00b894", "#ffffff"),
    "海尔":     ("#00529b", "#ffffff"),
    "格力":     ("#00b894", "#ffffff"),
    "美的":     ("#00b894", "#ffffff"),
    "tcl":      ("#e4002b", "#ffffff"),
    "海信":     ("#00529b", "#ffffff"),
    "惠普":     ("#007db8", "#ffffff"),
    "微软":     ("#7c7c7c", "#ffffff"),
    "先锋":     ("#e4002b", "#ffffff"),
    "三得利":   ("#00529b", "#ffffff"),
    "百草味":   ("#e4002b", "#ffffff"),
    "奥利奥":   ("#00529b", "#ffffff"),
    "乐事":     ("#ffd700", "#000000"),
    "安慕希":   ("#00529b", "#ffffff"),
    "特仑苏":   ("#00529b", "#ffffff"),
    "帮宝适":   ("#ffc0cb", "#333333"),
    "花王":     ("#00529b", "#ffffff"),
    "好奇":     ("#ffc0cb", "#333333"),
    "美赞臣":   ("#00529b", "#ffffff"),
    "惠氏":     ("#00529b", "#ffffff"),
    "火火兔":   ("#ff6900", "#ffffff"),
    "泡泡玛特": ("#e4002b", "#ffffff"),
    "万代":     ("#00529b", "#ffffff"),
    "妙洁":     ("#00b894", "#ffffff"),
    "三只松鼠": ("#e4002b", "#ffffff"),
    "良品铺子": ("#e4002b", "#ffffff"),
    "百草味":   ("#e4002b", "#ffffff"),
    "新安怡":   ("#ffc0cb", "#333333"),
    "salomon":  ("#1a1a1a", "#ffffff"),
    "arc'teryx":("#1a1a1a", "#ffffff"),
    "始祖鸟":   ("#1a1a1a", "#ffffff"),
    "mammut":   ("#1a1a1a", "#ffffff"),
    "猛犸象":   ("#1a1a1a", "#ffffff"),
    "la sportiva": ("#e4002b", "#ffffff"),
    "osprey":   ("#00b894", "#ffffff"),
    "gregory":  ("#1a1a1a", "#ffffff"),
    "msr":      ("#ff6900", "#ffffff"),
    "black diamond": ("#1a1a1a", "#ffffff"),
    "polar":    ("#00529b", "#ffffff"),
    "under armour": ("#1a1a1a", "#ffffff"),
    "安德玛":   ("#1a1a1a", "#ffffff"),
    "giant":    ("#00b894", "#ffffff"),
    "捷安特":   ("#00b894", "#ffffff"),
    "trek":     ("#e4002b", "#ffffff"),
    "崔克":     ("#e4002b", "#ffffff"),
    "keep":     ("#4caf50", "#ffffff"),
    "asics":    ("#e4002b", "#ffffff"),
    "speedo":   ("#00529b", "#ffffff"),
    "斯伯丁":   ("#ff6900", "#ffffff"),
    "红双喜":   ("#e4002b", "#ffffff"),
    "尤尼克斯": ("#00529b", "#ffffff"),
    "yonex":    ("#00529b", "#ffffff"),
    "wilson":   ("#ffd700", "#000000"),
    "迪卡侬":   ("#00529b", "#ffffff"),
    "斑马":     ("#00529b", "#ffffff"),
    "zebra":    ("#00529b", "#ffffff"),
    "3m":       ("#e4002b", "#ffffff"),
    "levis":    ("#00529b", "#ffffff"),
    "新秀丽":   ("#1a1a1a", "#ffffff"),
    "samsonite": ("#1a1a1a", "#ffffff"),
    "mk":       ("#1a1a1a", "#ffffff"),
    "michael kors": ("#1a1a1a", "#ffffff"),
}


def get_brand_colors(name):
    name_lower = name.lower()
    for keyword, (bg, fg) in BRAND_COLORS.items():
        if keyword in name_lower:
            return bg, fg
    return "#e0e0e0", "#333333"


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    draw.pieslice([x1, y1, x1+2*radius, y1+2*radius], 180, 270, fill=fill)
    draw.pieslice([x2-2*radius, y1, x2, y1+2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2-2*radius, x1+2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*radius, y2-2*radius, x2, y2], 0, 90, fill=fill)


def parse_description(desc):
    """解析描述中的关键参数"""
    specs = []
    # 用逗号/，分割
    parts = re.split(r'[,，、]', desc)
    for part in parts:
        part = part.strip()
        if part:
            specs.append(part)
    return specs


def get_category_icon(category):
    """获取分类对应的图标文字"""
    icons = {
        "手机通讯": "📱",
        "电脑办公": "💻",
        "数码配件": "🔌",
        "智能设备": "⌚",
        "家用电器": "🏠",
        "厨房电器": "🍳",
        "个护美妆": "💄",
        "服饰鞋包": "👟",
        "食品饮料": "🥤",
        "生鲜果蔬": "🍎",
        "运动户外": "🏃",
        "家居日用": "🛋️",
        "图书文具": "📚",
        "母婴玩具": "🧸",
    }
    return icons.get(category, "📦")


def generate_detail_image(name, description, category, price, output_path):
    """生成单个商品的详情介绍图"""
    bg_hex, fg_hex = get_brand_colors(name)
    bg_color = hex_to_rgb(bg_hex)
    fg_color = hex_to_rgb(fg_hex)

    # 图片尺寸: 800 x 1000
    W, H = 800, 1000
    img = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ── 顶部品牌色横幅 ──
    draw.rectangle([0, 0, W, 180], fill=bg_color)

    # 品牌名 / 商品名
    font_brand = get_font(20)
    font_name = get_font(36)
    font_price = get_font(28)
    font_spec = get_font(22)
    font_small = get_font(18)
    font_tiny = get_font(14)

    # 商品名 (白色)
    # 截断过长的名称
    display_name = name if len(name) <= 15 else name[:15] + "..."
    draw.text((40, 40), display_name, fill=(255, 255, 255), font=font_name)

    # 分类标签
    icon = get_category_icon(category)
    cat_text = f"{icon} {category}"
    draw.text((40, 90), cat_text, fill=(255, 255, 255, 200), font=font_small)

    # 价格
    price_yuan = f"¥{price / 100:.0f}"
    draw.text((40, 125), price_yuan, fill=(255, 255, 255), font=font_price)

    # ── 核心卖点区 ──
    y = 200
    draw.text((40, y), "✦ 核心卖点", fill=bg_color, font=font_spec)
    y += 40

    specs = parse_description(description)
    for i, spec in enumerate(specs[:6]):
        # 卖点卡片
        card_y = y + i * 48
        draw_rounded_rect(draw, (40, card_y, W - 40, card_y + 40), 8, (*bg_color, 15) if len(bg_color) == 3 else bg_color)

        # 用浅色背景
        light_bg = tuple(min(c + 240, 255) for c in bg_color)
        draw_rounded_rect(draw, (40, card_y, W - 40, card_y + 40), 8, light_bg)

        # 序号
        num_text = f"0{i+1}"
        draw.text((55, card_y + 8), num_text, fill=bg_color, font=font_small)

        # 文字
        draw.text((95, card_y + 8), spec, fill=(51, 51, 51), font=font_small)

    # ── 分隔线 ──
    sep_y = 200 + 40 + 6 * 48 + 20
    draw.line([(40, sep_y), (W - 40, sep_y)], fill=(230, 230, 230), width=2)

    # ── 规格参数表 ──
    spec_y = sep_y + 20
    draw.text((40, spec_y), "📋 规格参数", fill=bg_color, font=font_spec)
    spec_y += 40

    # 构建参数表
    params = []
    # 从描述中提取有数字的参数
    for spec in specs:
        if any(c.isdigit() for c in spec) or 'mAh' in spec or 'GB' in spec or 'TB' in spec or '寸' in spec or 'mm' in spec or 'kg' in spec or 'W' in spec:
            # 尝试分割 key-value
            if len(spec) > 6:
                params.append(spec)

    if not params:
        params = specs[:4]

    for i, param in enumerate(params[:5]):
        row_y = spec_y + i * 36
        # 斑马纹
        if i % 2 == 0:
            draw.rectangle([40, row_y, W - 40, row_y + 32], fill=(248, 248, 248))
        draw.text((55, row_y + 5), param, fill=(80, 80, 80), font=font_small)

    # ── 底部品牌标识 ──
    footer_y = H - 60
    draw.rectangle([0, footer_y, W, H], fill=bg_color)
    draw.text((40, footer_y + 18), f"MallHub · {name}", fill=(255, 255, 255), font=font_small)

    # 保存
    img.save(output_path, "JPEG", quality=90)


def sanitize_filename(name):
    clean = re.sub(r'[^\w一-鿿]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean.lower()


def extract_products(seed_path):
    with open(seed_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'Product\(.*?name="([^"]+)".*?description="([^"]+)".*?category="([^"]+)".*?price=(\d+)'
    matches = re.findall(pattern, content, re.DOTALL)

    products = []
    for name, desc, cat, price in matches:
        products.append({"name": name, "description": desc, "category": cat, "price": int(price)})
    return products


def main():
    products = extract_products(str(SEED_FILE))
    print(f"共 {len(products)} 个商品\n")

    generated = 0
    skipped = 0

    for i, p in enumerate(products, 1):
        filename = sanitize_filename(p["name"])
        output_path = OUTPUT_DIR / f"{filename}.jpg"

        if output_path.exists():
            skipped += 1
            continue

        print(f"[{i:3d}/{len(products)}] 生成: {p['name']}")
        generate_detail_image(
            p["name"], p["description"], p["category"], p["price"], output_path
        )
        generated += 1

    print(f"\n{'='*50}")
    print(f"完成!")
    print(f"  新生成: {generated}")
    print(f"  已存在: {skipped}")
    print(f"  输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
