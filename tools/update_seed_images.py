# -*- coding: utf-8 -*-
"""更新 seed.py 中所有商品的 image_url 为新生成的品牌图片"""
import re
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEED_FILE = Path(__file__).parent.parent / "backend" / "seed.py"
MAPPING_FILE = Path(__file__).parent.parent / "backend" / "static" / "products" / "final" / "image_mapping.json"


def main():
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    updated = 0
    not_found = 0

    for name, new_url in mapping.items():
        # 匹配 name="xxx" 的 Product 行中的 image_url
        # 使用更精确的替换：找到包含 name="xxx" 的行，替换其中的 image_url
        old_pattern = rf'(name="{re.escape(name)}".*?image_url=")[^"]+(")'
        new_content = re.sub(old_pattern, rf'\g<1>{new_url}\g<2>', content, count=1, flags=re.DOTALL)
        if new_content != content:
            content = new_content
            updated += 1
        else:
            not_found += 1
            print(f"  ⚠️ 未找到: {name}")

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n更新完成!")
    print(f"  已更新: {updated}")
    print(f"  未找到: {not_found}")
    print(f"  文件: {SEED_FILE}")


if __name__ == "__main__":
    main()
