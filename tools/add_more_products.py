# -*- coding: utf-8 -*-
"""批量添加新商品：生鲜果蔬、厨房电器、个护美妆、服饰鞋包"""
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User, Shop
from app.models.category import Category
from app.models.review import Review
from app.models.favorite import Favorite
from app.models.coupon import Coupon
from app.models.notification import Notification


# 新增商品: (店铺名, 商品名, 描述, 价格(分), 库存, 分类)
NEW_PRODUCTS = [
    # ═══ 生鲜果蔬 (+10) ═══
    ("居家生活馆", "丹东99草莓 2斤", "新鲜现摘，甜度高，果香浓郁", 5900, 30, "生鲜果蔬"),
    ("居家生活馆", "海南金煌芒 5斤", "个大肉厚，香甜多汁，产地直发", 3900, 40, "生鲜果蔬"),
    ("居家生活馆", "阳澄湖大闸蟹 4对", "公4两母3两，鲜活直达，礼盒装", 29900, 20, "生鲜果蔬"),
    ("居家生活馆", "内蒙古羊排 1kg", "草饲羊排，肉质鲜嫩，真空包装", 6900, 25, "生鲜果蔬"),
    ("居家生活馆", "三文鱼刺身 200g", "挪威进口，冰鲜到家，可做刺身", 4900, 30, "生鲜果蔬"),
    ("居家生活馆", "云南普洱茶 357g", "2024年古树春茶，生茶饼茶", 19900, 15, "生鲜果蔬"),
    ("居家生活馆", "新疆哈密瓜 2个", "脆甜多汁，产地直发", 2900, 35, "生鲜果蔬"),
    ("居家生活馆", "澳洲谷饲牛排 200g*4", "M3级雪花，原切眼肉", 12900, 20, "生鲜果蔬"),
    ("居家生活馆", "厄瓜多尔白虾 2kg", "大号15/20，船冻锁鲜", 8900, 25, "生鲜果蔬"),
    ("居家生活馆", "智利三文鱼柳 400g", "去骨去皮，真空包装，可煎可烤", 5900, 30, "生鲜果蔬"),

    # ═══ 厨房电器 (+7) ═══
    ("居家生活馆", "美的 破壁料理机", "1200W大功率，8叶刀头，冷热双杯", 59900, 25, "厨房电器"),
    ("居家生活馆", "九阳 空气炸锅 5L", "无油低脂，360°热风循环，触屏控制", 29900, 40, "厨房电器"),
    ("居家生活馆", "苏泊尔 电压力锅 5L", "双胆设计，智能预约，一键排气", 39900, 30, "厨房电器"),
    ("居家生活馆", "松下 面包机", "自动投料，25种菜单，可做酸奶", 89900, 15, "厨房电器"),
    ("居家生活馆", "小熊 养生壶 1.5L", "玻璃壶体，12大功能，保温24小时", 12900, 50, "厨房电器"),
    ("居家生活馆", "博朗 手持搅拌棒", "800W大功率，多档调速，配件丰富", 39900, 20, "厨房电器"),
    ("居家生活馆", "摩飞 多功能料理锅", "煎烤蒸煮一体，不粘涂层，可拆洗", 49900, 25, "厨房电器"),

    # ═══ 个护美妆 (+9) ═══
    ("美妆个护旗舰店", "珀莱雅 双抗精华", "虾青素+麦角硫因，抗氧抗糖，30ml", 19900, 40, "个护美妆"),
    ("美妆个护旗舰店", "薇诺娜 防晒乳 SPF50", "敏感肌专用，清透不油腻，50g", 16800, 35, "个护美妆"),
    ("美妆个护旗舰店", "完美日记 眼影盘", "9色大地色系，哑光珠光搭配", 12900, 50, "个护美妆"),
    ("美妆个护旗舰店", "花西子 蜜粉饼", "空气蜜粉，控油定妆，轻薄透气", 14900, 30, "个护美妆"),
    ("美妆个护旗舰店", "欧莱雅 玻尿酸洗面奶", "氨基酸温和洁面，保湿不紧绷，125ml", 7900, 60, "个护美妆"),
    ("美妆个护旗舰店", "修丽可 CE精华", "15%维C+维E+阿魏酸，抗氧化，30ml", 129900, 15, "个护美妆"),
    ("美妆个护旗舰店", "海蓝之谜 精粹水", "修护精华水，保湿舒缓，150ml", 119900, 10, "个护美妆"),
    ("美妆个护旗舰店", "阿玛尼 红管唇釉", "丝绒质地，持久显色，405号色", 32000, 25, "个护美妆"),
    ("美妆个护旗舰店", "科颜氏 高保湿面霜", "角鲨烷+冰川蛋白，深层保湿，50ml", 32000, 30, "个护美妆"),

    # ═══ 服饰鞋包 (+9) ═══
    ("运动户外专营店", "优衣库 轻薄羽绒服", "90%白鸭绒，轻量保暖，可收纳", 49900, 40, "服饰鞋包"),
    ("运动户外专营店", "Nike Air Max 270", "大气垫缓震，网面透气，休闲百搭", 99900, 25, "服饰鞋包"),
    ("运动户外专营店", "Adidas Stan Smith", "经典绿尾小白鞋，皮质鞋面", 69900, 30, "服饰鞋包"),
    ("运动户外专营店", "优衣库 摇粒绒夹克", "保暖舒适，轻量便携，多色可选", 14900, 50, "服饰鞋包"),
    ("运动户外专营店", "李宁 跑步鞋 飞电3", "䨻科技中底，碳板竞速，轻量化", 89900, 20, "服饰鞋包"),
    ("运动户外专营店", "安踏 C202 跑鞋", "氮科技中底，轻弹回弹，马拉松竞速", 59900, 25, "服饰鞋包"),
    ("运动户外专营店", "北面 1996 羽绒马甲", "700蓬鹅绒，轻量保暖，户外必备", 99900, 15, "服饰鞋包"),
    ("运动户外专营店", "Coach 蔻驰 托特包", "经典C字印花，大容量，通勤百搭", 299900, 10, "服饰鞋包"),
    ("运动户外专营店", "FILA 斐乐 老爹鞋", "复古增高，网面透气，情侣款", 59900, 30, "服饰鞋包"),
]


def main():
    db = SessionLocal()
    try:
        # 获取店铺映射
        shops = {s.name: s for s in db.query(Shop).all()}

        added = 0
        for shop_name, name, desc, price, stock, category in NEW_PRODUCTS:
            # 检查是否已存在
            existing = db.query(Product).filter(Product.name == name).first()
            if existing:
                print(f"  ⏭️ 已存在: {name}")
                continue

            shop = shops.get(shop_name)
            if not shop:
                print(f"  ⚠️ 未找到店铺: {shop_name}")
                continue

            p = Product(
                shop_id=shop.id,
                name=name,
                description=desc,
                price=price,
                stock=stock,
                category=category,
                image_url="/static/products/real_v2/placeholder.jpg"
            )
            db.add(p)
            added += 1
            print(f"  ✅ {name}")

        db.commit()
        print(f"\n新增完成: {added} 个商品")

        # 统计
        from sqlalchemy import func
        total = db.query(Product).count()
        cats = db.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
        print(f"\n当前总商品数: {total}")
        for cat, count in sorted(cats, key=lambda x: -x[1]):
            print(f"  {cat}: {count}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
