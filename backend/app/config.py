import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'market.db'}")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24 * 7

ALIPAY_APPID = os.getenv("ALIPAY_APPID", "")
ALIPAY_PRIVATE_KEY = os.getenv("ALIPAY_PRIVATE_KEY", "")
ALIPAY_PUBLIC_KEY = os.getenv("ALIPAY_PUBLIC_KEY", "")
ALIPAY_GATEWAY = os.getenv("ALIPAY_GATEWAY", "https://openapi-sandbox.dl.alipaydev.com/gateway.do")
ALIPAY_NOTIFY_URL = os.getenv("ALIPAY_NOTIFY_URL", "http://localhost:8000/api/payment/notify")
ALIPAY_RETURN_URL = os.getenv("ALIPAY_RETURN_URL", "http://localhost:5173/pay-result")

UPLOAD_DIR = BASE_DIR / "uploads"
