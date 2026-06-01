# -*- coding: utf-8 -*-
"""更新 seed.py 和数据库中的图片 URL 为 real_v2 版本"""
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

MAPPING_FILE = Path(__file__).parent.parent / "backend" / "static" / "products" / "real_v2" / "image_mapping.json"
SEED_FILE = Path(__file__).parent.parent / "backend" / "seed.py"


def update_seed():
    """更新 seed.py 中的 image_url"""
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    updated = 0
    for name, new_url in mapping.items():
        old_pattern = rf'(name="{re.escape(name)}".*?image_url=")[^"]+(")'
        new_content = re.sub(old_pattern, rf'\g<1>{new_url}\g<2>', content, count=1, flags=re.DOTALL)
        if new_content != content:
            content = new_content
            updated += 1

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"seed.py 更新: {updated} 个商品")


def update_database():
    """更新数据库中的 image_url"""
    from app.database import SessionLocal
    from app.models.product import Product
    from app.models.user import User, Shop
    from app.models.category import Category
    from app.models.review import Review
    from app.models.favorite import Favorite
    from app.models.coupon import Coupon
    from app.models.notification import Notification

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    db = SessionLocal()
    try:
        products = db.query(Product).all()
        updated = 0
        for p in products:
            if p.name in mapping:
                new_url = mapping[p.name]
                if p.image_url != new_url:
                    p.image_url = new_url
                    updated += 1
        db.commit()
        print(f"数据库更新: {updated} 个商品")
    finally:
        db.close()


if __name__ == "__main__":
    update_seed()
    update_database()
    print("全部完成!")
