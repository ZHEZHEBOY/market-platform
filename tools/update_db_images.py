# -*- coding: utf-8 -*-
"""更新数据库中所有商品的 image_url"""
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User, Shop
from app.models.category import Category
from app.models.review import Review
from app.models.favorite import Favorite
from app.models.coupon import Coupon
from app.models.notification import Notification

MAPPING_FILE = Path(__file__).parent.parent / "backend" / "static" / "products" / "final" / "image_mapping.json"


def main():
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    db = SessionLocal()
    updated = 0

    try:
        products = db.query(Product).all()
        print(f"数据库中共有 {len(products)} 个商品\n")

        for product in products:
            if product.name in mapping:
                new_url = mapping[product.name]
                if product.image_url != new_url:
                    product.image_url = new_url
                    updated += 1
                    print(f"  ✅ {product.name} -> {new_url}")

        db.commit()
        print(f"\n更新完成! 共更新 {updated} 个商品")
    finally:
        db.close()


if __name__ == "__main__":
    main()
