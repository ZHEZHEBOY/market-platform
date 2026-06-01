# -*- coding: utf-8 -*-
"""为数据库中所有商品生成详情图"""
import sys, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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
    '北面': ('#1a1a1a', '#ffffff'), 'thenorthface': ('#1a1a1a', '#ffffff'),
    '优衣库': ('#e4002b', '#ffffff'), 'uniqlo': ('#e4002b', '#ffffff'),
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
    'sanDisk': ('#e4002b', '#ffffff'), 'sandisk': ('#e4002b', '#ffffff'),
    'wd': ('#00529b', '#ffffff'), 'gskill': ('#e4002b', '#ffffff'),
    'micrsoft': ('#7c7c7c', '#ffffff'), 'hp': ('#007db8', '#ffffff'),
    '惠普': ('#007db8', '#ffffff'), '微软': ('#7c7c7c', '#ffffff'),
    '贝尔金': ('#00b894', '#ffffff'), 'belkin': ('#00b894', '#ffffff'),
    '倍思': ('#1a73e8', '#ffffff'), 'baseus': ('#1a73e8', '#ffffff'),
    '戴尔': ('#007db8', '#ffffff'), 'apple watch': ('#1a1a1a', '#f5f5f7'),
    'apple pencil': ('#1a1a1a', '#f5f5f7'), 'magsafe': ('#1a1a1a', '#f5f5f7'),
    'vision pro': ('#1a1a1a', '#f5f5f7'), 'macbook': ('#1a1a1a', '#f5f5f7'),
    'iphone': ('#1a1a1a', '#f5f5f7'), 'ipad': ('#1a1a1a', '#f5f5f7'),
    'airpods': ('#1a1a1a', '#f5f5f7'), 'homepod': ('#1a1a1a', '#f5f5f7'),
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

def rounded_rect(draw, xy, r, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+r, y1, x2-r, y2], fill=fill)
    draw.rectangle([x1, y1+r, x2, y2-r], fill=fill)
    draw.pieslice([x1, y1, x1+2*r, y1+2*r], 180, 270, fill=fill)
    draw.pieslice([x2-2*r, y1, x2, y1+2*r], 270, 360, fill=fill)
    draw.pieslice([x1, y2-2*r, x1+2*r, y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*r, y2-2*r, x2, y2], 0, 90, fill=fill)

def sanitize(name):
    clean = re.sub(r'[^\w一-鿿]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean.lower()

def gen(name, desc, cat, price, path):
    bg_hex, fg_hex = get_colors(name)
    bg = hex_rgb(bg_hex)
    W, H = 800, 1000
    img = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    fn = get_font(36); fp = get_font(28); fs = get_font(22); fm = get_font(18)

    d.rectangle([0, 0, W, 180], fill=bg)
    dn = name[:15] + '...' if len(name) > 15 else name
    d.text((40, 40), dn, fill=(255,255,255), font=fn)
    d.text((40, 90), f'{ICONS.get(cat, "📦")} {cat}', fill=(255,255,255), font=fm)
    d.text((40, 125), f'¥{price/100:.0f}', fill=(255,255,255), font=fp)

    y = 200
    d.text((40, y), '✦ 核心卖点', fill=bg, font=fs); y += 40
    specs = [p.strip() for p in re.split(r'[,，、]', desc) if p.strip()]
    for i, s in enumerate(specs[:6]):
        cy = y + i * 48
        lt = tuple(min(c+240, 255) for c in bg)
        rounded_rect(d, (40, cy, W-40, cy+40), 8, lt)
        d.text((55, cy+8), f'0{i+1}', fill=bg, font=fm)
        d.text((95, cy+8), s, fill=(51,51,51), font=fm)

    sy = 200 + 40 + 6*48 + 20
    d.line([(40, sy), (W-40, sy)], fill=(230,230,230), width=2)

    py = sy + 20
    d.text((40, py), '📋 规格参数', fill=bg, font=fs); py += 40
    params = [s for s in specs if any(c.isdigit() for c in s) or 'mAh' in s or 'GB' in s][:5]
    if not params: params = specs[:4]
    for i, p in enumerate(params[:5]):
        ry = py + i * 36
        if i % 2 == 0: d.rectangle([40, ry, W-40, ry+32], fill=(248,248,248))
        d.text((55, ry+5), p, fill=(80,80,80), font=fm)

    fy = H - 60
    d.rectangle([0, fy, W, H], fill=bg)
    d.text((40, fy+18), f'MallHub · {name}', fill=(255,255,255), font=fm)
    img.save(path, 'JPEG', quality=90)

db = SessionLocal()
try:
    products = db.query(Product).all()
    generated = 0
    for p in products:
        fname = sanitize(p.name) + '.jpg'
        out = OUTPUT_DIR / fname
        if out.exists():
            if not p.detail_image:
                p.detail_image = f'/static/products/details/{fname}'
            continue
        print(f'生成: {p.name}')
        gen(p.name, p.description or '', p.category or '', p.price, out)
        p.detail_image = f'/static/products/details/{fname}'
        generated += 1
    db.commit()
    with_detail = db.query(Product).filter(Product.detail_image != '').count()
    total = db.query(Product).count()
    print(f'\n完成! 新生成: {generated}, 有详情图: {with_detail}/{total}')
finally:
    db.close()
