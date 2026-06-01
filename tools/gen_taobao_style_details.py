# -*- coding: utf-8 -*-
"""
生成淘宝风格的商品详情图
- 产品主图作为背景
- 叠加功能卖点文字
- 规格参数卡片
- 品牌配色装饰
"""
import sys, re, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User, Shop
from app.models.category import Category
from app.models.review import Review
from app.models.favorite import Favorite
from app.models.coupon import Coupon
from app.models.notification import Notification

OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "details"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PRODUCT_IMG_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "real_v2"

FONT_PATHS = ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simhei.ttf']

def get_font(size):
    for fp in FONT_PATHS:
        try: return ImageFont.truetype(fp, size)
        except: continue
    return ImageFont.load_default()

BRAND_COLORS = {
    'apple': ('#1a1a1a', '#f5f5f7'), 'iphone': ('#1a1a1a', '#f5f5f7'),
    'macbook': ('#1a1a1a', '#f5f5f7'), 'ipad': ('#1a1a1a', '#f5f5f7'),
    'airpods': ('#1a1a1a', '#f5f5f7'), 'homepod': ('#1a1a1a', '#f5f5f7'),
    'xiaomi': ('#ff6900', '#ffffff'), '小米': ('#ff6900', '#ffffff'),
    'redmi': ('#ff6900', '#ffffff'), '华为': ('#cf0a2c', '#ffffff'),
    'huawei': ('#cf0a2c', '#ffffff'), '三星': ('#1428a0', '#ffffff'),
    'samsung': ('#1428a0', '#ffffff'), 'oppo': ('#1a73e8', '#ffffff'),
    'vivo': ('#415fff', '#ffffff'), '一加': ('#eb0028', '#ffffff'),
    '荣耀': ('#0ab4e8', '#ffffff'), '索尼': ('#1a1a1a', '#ffffff'),
    'sony': ('#1a1a1a', '#ffffff'), '戴森': ('#6b21a8', '#ffffff'),
    'dyson': ('#6b21a8', '#ffffff'), 'nike': ('#1a1a1a', '#ffffff'),
    'adidas': ('#1a1a1a', '#ffffff'), '联想': ('#e4002b', '#ffffff'),
    'lenovo': ('#e4002b', '#ffffff'), 'thinkpad': ('#e4002b', '#ffffff'),
    'legion': ('#e4002b', '#ffffff'), '戴尔': ('#007db8', '#ffffff'),
    'dell': ('#007db8', '#ffffff'), 'xps': ('#007db8', '#ffffff'),
    '华硕': ('#ff005a', '#ffffff'), 'rog': ('#ff005a', '#ffffff'),
    '罗技': ('#00b894', '#ffffff'), 'logitech': ('#00b894', '#ffffff'),
    '雷蛇': ('#44d62c', '#000000'), 'razer': ('#44d62c', '#000000'),
    '飞利浦': ('#0ab4e8', '#ffffff'), 'philips': ('#0ab4e8', '#ffffff'),
    '美的': ('#00b894', '#ffffff'), '九阳': ('#ff6900', '#ffffff'),
    '松下': ('#00529b', '#ffffff'), 'panasonic': ('#00529b', '#ffffff'),
    '迪卡侬': ('#00529b', '#ffffff'), 'decathlon': ('#00529b', '#ffffff'),
    'jbl': ('#ff6900', '#ffffff'), '乐高': ('#ffd700', '#000000'),
    'lego': ('#ffd700', '#000000'), 'ikea': ('#00529b', '#ffffff'),
    '宜家': ('#00529b', '#ffffff'), 'muji': ('#f5f5dc', '#333333'),
    '无印': ('#f5f5dc', '#333333'), '星巴克': ('#00704a', '#ffffff'),
    'dior': ('#e4002b', '#ffffff'), '迪奥': ('#e4002b', '#ffffff'),
    'chanel': ('#1a1a1a', '#ffffff'), '香奈儿': ('#1a1a1a', '#ffffff'),
    'sk-ii': ('#e4002b', '#ffffff'), '兰蔻': ('#00529b', '#ffffff'),
    'lancome': ('#00529b', '#ffffff'), 'surface': ('#7c7c7c', '#ffffff'),
    'garmin': ('#00b894', '#ffffff'), 'bose': ('#1a1a1a', '#ffffff'),
    'marshall': ('#1a1a1a', '#ffffff'), 'lg': ('#a50034', '#ffffff'),
    'realme': ('#ffc700', '#000000'), 'iqoo': ('#1a73e8', '#ffffff'),
    '魅族': ('#0ab4e8', '#ffffff'), 'meizu': ('#0ab4e8', '#ffffff'),
    'anker': ('#0ab4e8', '#ffffff'), '安克': ('#0ab4e8', '#ffffff'),
    '科沃斯': ('#00b894', '#ffffff'), 'ecovacs': ('#00b894', '#ffffff'),
    '西门子': ('#1a1a1a', '#ffffff'), 'tcl': ('#e4002b', '#ffffff'),
    '海信': ('#00529b', '#ffffff'), '李宁': ('#e4002b', '#ffffff'),
    '安踏': ('#e4002b', '#ffffff'), '斐乐': ('#1a1a1a', '#ffffff'),
    'fila': ('#1a1a1a', '#ffffff'), 'coach': ('#8b4513', '#ffffff'),
    '蔻驰': ('#8b4513', '#ffffff'), '珀莱雅': ('#e4002b', '#ffffff'),
    '薇诺娜': ('#00b894', '#ffffff'), '完美日记': ('#e4002b', '#ffffff'),
    '花西子': ('#ff6900', '#ffffff'), '欧莱雅': ('#1a1a1a', '#ffffff'),
    '修丽可': ('#00529b', '#ffffff'), '海蓝之谜': ('#00529b', '#ffffff'),
    '阿玛尼': ('#1a1a1a', '#ffffff'), '科颜氏': ('#00529b', '#ffffff'),
    '北面': ('#1a1a1a', '#ffffff'), '优衣库': ('#e4002b', '#ffffff'),
    '匡威': ('#1a1a1a', '#ffffff'), 'converse': ('#1a1a1a', '#ffffff'),
    'lululemon': ('#1a1a1a', '#ffffff'), '三只松鼠': ('#e4002b', '#ffffff'),
    '良品铺子': ('#e4002b', '#ffffff'), '元气森林': ('#00b894', '#ffffff'),
    '三顿半': ('#1a1a1a', '#ffffff'), '瑞幸': ('#00529b', '#ffffff'),
    '农夫山泉': ('#00b894', '#ffffff'), '可口可乐': ('#e4002b', '#ffffff'),
    '百事可乐': ('#00529b', '#ffffff'), '蒙牛': ('#00529b', '#ffffff'),
    '伊利': ('#00529b', '#ffffff'), '飞鹤': ('#00529b', '#ffffff'),
    '费雪': ('#e4002b', '#ffffff'), '好孩子': ('#0ab4e8', '#ffffff'),
    '贝亲': ('#ffc0cb', '#333333'), '得力': ('#e4002b', '#ffffff'),
    '晨光': ('#e4002b', '#ffffff'), '蓝月亮': ('#00529b', '#ffffff'),
    '维达': ('#00b894', '#ffffff'), '水星': ('#00529b', '#ffffff'),
    '全棉时代': ('#ffc0cb', '#333333'), '网易严选': ('#e4002b', '#ffffff'),
    '芙丽芳丝': ('#ffc0cb', '#333333'), '敷尔佳': ('#ffc0cb', '#333333'),
    '安耐晒': ('#ffd700', '#000000'), '太力': ('#00b894', '#ffffff'),
    '小熊': ('#ff6900', '#ffffff'), '博朗': ('#1a1a1a', '#ffffff'),
    '摩飞': ('#ff6900', '#ffffff'), '苏泊尔': ('#00b894', '#ffffff'),
    '格兰仕': ('#e4002b', '#ffffff'), '石头': ('#1a1a1a', '#ffffff'),
    '追觅': ('#0ab4e8', '#ffffff'), '绿联': ('#00b894', '#ffffff'),
    '明基': ('#00b894', '#ffffff'), 'benq': ('#00b894', '#ffffff'),
    '金士顿': ('#e4002b', '#ffffff'), 'kingston': ('#e4002b', '#ffffff'),
    '西部数据': ('#00529b', '#ffffff'), '芝奇': ('#e4002b', '#ffffff'),
    '佳明': ('#00b894', '#ffffff'), '海尔': ('#00529b', '#ffffff'),
    '格力': ('#00b894', '#ffffff'), 'salomon': ('#1a1a1a', '#ffffff'),
    '始祖鸟': ('#1a1a1a', '#ffffff'), 'mammut': ('#1a1a1a', '#ffffff'),
    'osprey': ('#00b894', '#ffffff'), 'gregory': ('#1a1a1a', '#ffffff'),
    'polar': ('#00529b', '#ffffff'), 'under armour': ('#1a1a1a', '#ffffff'),
    '安德玛': ('#1a1a1a', '#ffffff'), 'giant': ('#00b894', '#ffffff'),
    '捷安特': ('#00b894', '#ffffff'), 'trek': ('#e4002b', '#ffffff'),
    '崔克': ('#e4002b', '#ffffff'), 'keep': ('#4caf50', '#ffffff'),
    'asics': ('#e4002b', '#ffffff'), 'speedo': ('#00529b', '#ffffff'),
    '斯伯丁': ('#ff6900', '#ffffff'), '红双喜': ('#e4002b', '#ffffff'),
    '尤尼克斯': ('#00529b', '#ffffff'), 'yonex': ('#00529b', '#ffffff'),
    'wilson': ('#ffd700', '#000000'), '斑马': ('#00529b', '#ffffff'),
    '3m': ('#e4002b', '#ffffff'), 'levis': ('#00529b', '#ffffff'),
    '新秀丽': ('#1a1a1a', '#ffffff'), 'samsonite': ('#1a1a1a', '#ffffff'),
    'mk': ('#1a1a1a', '#ffffff'), '百草味': ('#e4002b', '#ffffff'),
    '奥利奥': ('#00529b', '#ffffff'), '乐事': ('#ffd700', '#000000'),
    '安慕希': ('#00529b', '#ffffff'), '特仑苏': ('#00529b', '#ffffff'),
    '帮宝适': ('#ffc0cb', '#333333'), '花王': ('#00529b', '#ffffff'),
    '好奇': ('#ffc0cb', '#333333'), '美赞臣': ('#00529b', '#ffffff'),
    '惠氏': ('#00529b', '#ffffff'), '火火兔': ('#ff6900', '#ffffff'),
    '泡泡玛特': ('#e4002b', '#ffffff'), '万代': ('#00529b', '#ffffff'),
    '妙洁': ('#00b894', '#ffffff'), '新安怡': ('#ffc0cb', '#333333'),
    '三得利': ('#00529b', '#ffffff'), '百岁山': ('#00529b', '#ffffff'),
    '先锋': ('#e4002b', '#ffffff'), 'la sportiva': ('#e4002b', '#ffffff'),
    'black diamond': ('#1a1a1a', '#ffffff'), 'msr': ('#ff6900', '#ffffff'),
    'elgato': ('#1a1a1a', '#ffffff'), 'hhkb': ('#1a1a1a', '#ffffff'),
    'cherry': ('#1a1a1a', '#ffffff'), 'new balance': ('#e4002b', '#ffffff'),
    'sandisk': ('#e4002b', '#ffffff'), 'wd': ('#00529b', '#ffffff'),
    'gskill': ('#e4002b', '#ffffff'), 'hp': ('#007db8', '#ffffff'),
    '惠普': ('#007db8', '#ffffff'), '微软': ('#7c7c7c', '#ffffff'),
    '贝尔金': ('#00b894', '#ffffff'), 'belkin': ('#00b894', '#ffffff'),
    '倍思': ('#1a73e8', '#ffffff'), 'baseus': ('#1a73e8', '#ffffff'),
    'apple watch': ('#1a1a1a', '#f5f5f7'), 'apple pencil': ('#1a1a1a', '#f5f5f7'),
    'magsafe': ('#1a1a1a', '#f5f5f7'), 'vision pro': ('#1a1a1a', '#f5f5f7'),
}

ICONS = {
    '手机通讯': '📱', '电脑办公': '💻', '数码配件': '🔌', '智能设备': '⌚',
    '家用电器': '🏠', '厨房电器': '🍳', '个护美妆': '💄', '服饰鞋包': '👟',
    '食品饮料': '🥤', '生鲜果蔬': '🍎', '运动户外': '🏃', '家居日用': '🛋️',
    '图书文具': '📚', '母婴玩具': '🧸',
}

def get_colors(name):
    for kw, c in BRAND_COLORS.items():
        if kw in name.lower():
            return c
    return '#e0e0e0', '#333333'

def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def sanitize(name):
    clean = re.sub(r'[^\w一-鿿]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean.lower()

def find_product_image(name):
    """查找商品主图"""
    fname = sanitize(name) + '.jpg'
    path = PRODUCT_IMG_DIR / fname
    if path.exists():
        return path
    return None

def crop_center_square(img, size=400):
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    return img.crop((left, top, left + min_dim, top + min_dim)).resize((size, size), Image.LANCZOS)

def draw_rounded_rect(draw, xy, r, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+r, y1, x2-r, y2], fill=fill)
    draw.rectangle([x1, y1+r, x2, y2-r], fill=fill)
    draw.pieslice([x1, y1, x1+2*r, y1+2*r], 180, 270, fill=fill)
    draw.pieslice([x2-2*r, y1, x2, y1+2*r], 270, 360, fill=fill)
    draw.pieslice([x1, y2-2*r, x1+2*r, y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*r, y2-2*r, x2, y2], 0, 90, fill=fill)

def gen_taobao_detail(name, desc, cat, price, product_img_path, output_path):
    """生成淘宝风格详情图"""
    bg_hex, fg_hex = get_colors(name)
    bg = hex_rgb(bg_hex)
    fg = hex_rgb(fg_hex)

    W, H = 800, 1200
    img = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    fn = get_font(32); fp = get_font(26); fs = get_font(20); fm = get_font(16); ft = get_font(14)

    # ── 顶部品牌色横幅 ──
    draw.rectangle([0, 0, W, 120], fill=bg)
    dn = name[:16] + '...' if len(name) > 16 else name
    draw.text((30, 20), dn, fill=(255,255,255), font=fn)
    icon = ICONS.get(cat, '📦')
    draw.text((30, 65), f'{icon} {cat}', fill=(255,255,255), font=fm)
    draw.text((W-200, 30), f'¥{price/100:.0f}', fill=(255,255,255), font=fp)

    # ── 产品主图区域 ──
    img_y = 140
    if product_img_path and product_img_path.exists():
        try:
            prod_img = Image.open(product_img_path).convert('RGB')
            prod_img = crop_center_square(prod_img, 300)
            # 居中放置
            img.paste(prod_img, (250, img_y))
        except:
            pass
    else:
        # 没有产品图，画一个占位
        draw.rectangle([250, img_y, 550, img_y+300], fill=(245,245,245), outline=(220,220,220))
        draw.text((350, img_y+140), '📦', fill=(180,180,180), font=get_font(48))

    # ── 产品名称 (产品图下方) ──
    name_y = img_y + 320
    draw.text((30, name_y), name, fill=(33,33,33), font=fn)

    # ── 价格标签 ──
    price_y = name_y + 45
    draw_rounded_rect(draw, (30, price_y, 200, price_y+40), 6, (255, 235, 235))
    draw.text((45, price_y+8), f'¥{price/100:.0f}', fill=(228, 57, 60), font=fp)

    # ── 分隔线 ──
    sep_y = price_y + 60
    draw.line([(30, sep_y), (W-30, sep_y)], fill=(240,240,240), width=2)

    # ── 核心卖点 ──
    feat_y = sep_y + 20
    draw.text((30, feat_y), '✦ 核心卖点', fill=bg, font=fs)
    feat_y += 35

    specs = [p.strip() for p in re.split(r'[,，、]', desc) if p.strip()]
    for i, spec in enumerate(specs[:5]):
        cy = feat_y + i * 42
        # 卖点条
        light = tuple(min(c+245, 255) for c in bg)
        draw_rounded_rect(draw, (30, cy, W-30, cy+36), 6, light)
        # 序号圆点
        draw.ellipse((42, cy+8, 58, cy+24), fill=bg)
        draw.text((46, cy+9), str(i+1), fill=(255,255,255), font=ft)
        # 文字
        draw.text((68, cy+8), spec, fill=(60,60,60), font=fm)

    # ── 规格参数表 ──
    spec_y = feat_y + 5 * 42 + 20
    draw.line([(30, spec_y), (W-30, spec_y)], fill=(240,240,240), width=2)
    spec_y += 15
    draw.text((30, spec_y), '📋 商品规格', fill=bg, font=fs)
    spec_y += 35

    # 表头
    draw_rounded_rect(draw, (30, spec_y, W-30, spec_y+32), 4, bg)
    draw.text((50, spec_y+6), '参数', fill=(255,255,255), font=fm)
    draw.text((350, spec_y+6), '详情', fill=(255,255,255), font=fm)
    spec_y += 36

    # 参数行
    params = [s for s in specs if len(s) > 3][:6]
    if not params:
        params = specs[:5]
    for i, p in enumerate(params):
        ry = spec_y + i * 32
        if i % 2 == 0:
            draw.rectangle([30, ry, W-30, ry+30], fill=(248,248,248))
        # 分割 key: value
        if ':' in p:
            k, v = p.split(':', 1)
            draw.text((50, ry+6), k.strip(), fill=(80,80,80), font=fm)
            draw.text((350, ry+6), v.strip(), fill=(60,60,60), font=fm)
        elif '：' in p:
            k, v = p.split('：', 1)
            draw.text((50, ry+6), k.strip(), fill=(80,80,80), font=fm)
            draw.text((350, ry+6), v.strip(), fill=(60,60,60), font=fm)
        else:
            draw.text((50, ry+6), p, fill=(60,60,60), font=fm)

    # ── 底部品牌条 ──
    footer_y = H - 50
    draw.rectangle([0, footer_y, W, H], fill=bg)
    draw.text((30, footer_y+15), f'MallHub 正品保障 · {name}', fill=(255,255,255), font=fm)

    img.save(output_path, 'JPEG', quality=90)


def main():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        generated = 0
        skipped = 0

        for i, p in enumerate(products, 1):
            fname = sanitize(p.name) + '.jpg'
            out = OUTPUT_DIR / fname

            # 查找产品主图
            prod_img = find_product_image(p.name)

            # 重新生成所有详情图（覆盖旧的）
            print(f'[{i:3d}/{len(products)}] 生成: {p.name}')
            gen_taobao_detail(
                p.name, p.description or '', p.category or '',
                p.price, prod_img, out
            )
            p.detail_image = f'/static/products/details/{fname}'
            generated += 1

        db.commit()
        print(f'\n完成! 生成: {generated}')
    finally:
        db.close()


if __name__ == '__main__':
    main()
