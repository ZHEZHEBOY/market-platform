# -*- coding: utf-8 -*-
"""更新数据库中的商品信息为2026年最新款"""
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

# 商品更新映射: (旧名称, 新名称, 新描述, 新价格)
UPDATES = [
    # 手机通讯
    ("小米14 Ultra", "小米17 Ultra", "骁龙8至尊版，徕卡光学镜头，2K AMOLED屏，5500mAh电池，120W快充", 599900),
    ("iPhone 16 Pro", "iPhone 17 Pro", "A19 Pro芯片，钛金属设计，4800万像素，5倍光学变焦，8GB内存", 899900),
    ("华为 Mate 70", "华为 Mate 80", "麒麟芯片，鸿蒙系统，5000万像素超光谱摄像头", 599900),
    ("三星 Galaxy S25 Ultra", "三星 Galaxy S26 Ultra", "骁龙8至尊版，2亿像素AI相机，钛金属框架，S Pen", 1099900),
    ("OPPO Find X8", "OPPO Find X9", "天玑9400+，哈苏影像，5800mAh电池，IP69防水", 449900),
    ("vivo X200 Pro", "vivo X300 Pro", "天玑9400+，蔡司影像，6000mAh蓝海电池，IP69防水", 499900),
    ("一加 13", "一加 14", "骁龙8至尊版，哈苏影像，6200mAh电池，100W快充", 449900),
    ("荣耀 Magic7 Pro", "荣耀 Magic8 Pro", "骁龙8至尊版，鹰眼相机，5850mAh电池，100W快充", 499900),
    ("小米14", "小米17", "骁龙8至尊版，徕卡光学，5000mAh电池，100W快充", 399900),
    ("Redmi K80 Pro", "Redmi K90 Pro", "骁龙8至尊版，2K屏，6500mAh电池，120W快充", 349900),
    ("realme GT7 Pro", "realme GT8 Pro", "骁龙8至尊版，IMX906主摄，6500mAh电池，120W快充", 369900),
    ("iQOO 13", "iQOO 14", "骁龙8至尊版，自研电竞芯片Q3，6200mAh电池，120W快充", 429900),
    ("魅族 21 Pro", "魅族 22 Pro", "骁龙8至尊版，超声波指纹，5500mAh电池，80W快充", 399900),
    ("ROG 游戏手机 9", "ROG 游戏手机 10", "骁龙8至尊版，185Hz电竞屏，6500mAh电池，AirTrigger", 629900),
    ("三星 Galaxy Z Fold6", "三星 Galaxy Z Fold7", "骁龙8至尊版，7.6英寸折叠屏，S Pen支持，IPX8防水", 1499900),
    ("三星 Galaxy Z Flip6", "三星 Galaxy Z Flip7", "骁龙8至尊版，6.7英寸折叠屏，Flex Window外屏", 849900),
    ("iPhone 16", "iPhone 17", "A19芯片，4800万像素，操作按钮，USB-C", 699900),
    ("iPhone 16 Pro Max", "iPhone 17 Pro Max", "A19 Pro芯片，6.9英寸，5倍光学变焦，钛金属，大电池", 1099900),
    ("华为 Mate X6", "华为 Mate X7", "麒麟芯片，6.4英寸外屏+7.85英寸内屏，XMAGE影像", 1399900),

    # 电脑办公
    ("MacBook Pro 14 M4", "MacBook Pro 14 M5", "M5 Pro芯片，24GB统一内存，512GB SSD，Liquid Retina XDR屏", 1599900),
    ("MacBook Air M4", "MacBook Air M5", "M5芯片，16GB统一内存，256GB SSD，18小时续航", 949900),

    # 数码配件
    ("iPhone 16 Pro 透明壳", "iPhone 17 Pro 透明壳", "MagSafe兼容，防摔军工认证，超薄0.8mm", 7900),

    # 智能设备
    ("小米手环 9", "小米手环 10", "1.62 AMOLED屏，血氧心率监测，150+运动模式，14天续航", 24900),
]


def main():
    db = SessionLocal()
    try:
        updated = 0
        for old_name, new_name, new_desc, new_price in UPDATES:
            product = db.query(Product).filter(Product.name == old_name).first()
            if product:
                product.name = new_name
                product.description = new_desc
                product.price = new_price
                updated += 1
                print(f"  ✅ {old_name} -> {new_name}")
            else:
                print(f"  ⚠️ 未找到: {old_name}")

        db.commit()
        print(f"\n数据库更新完成: {updated} 个商品")
    finally:
        db.close()


if __name__ == "__main__":
    main()
