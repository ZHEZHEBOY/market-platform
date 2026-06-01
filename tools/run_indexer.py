# -*- coding: utf-8 -*-
"""运行全量索引"""
import sys
import os
from pathlib import Path

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

from app.vector.indexer import reindex_all

if __name__ == "__main__":
    print("开始全量索引...")
    reindex_all()
    print("索引完成!")
