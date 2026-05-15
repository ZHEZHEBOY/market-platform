import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _read_secret(key: str, default: str = "") -> str:
    """Read a secret from env var. If value is a .pem file path, read its content."""
    val = os.getenv(key, default)
    if val and val.endswith(".pem"):
        pem_path = Path(val) if Path(val).is_absolute() else BASE_DIR / val
        if pem_path.exists():
            return pem_path.read_text().strip()
    return val


DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'market.db'}")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24 * 7

ALIPAY_APPID = _read_secret("ALIPAY_APPID")
ALIPAY_PRIVATE_KEY = _read_secret("ALIPAY_PRIVATE_KEY")
ALIPAY_PUBLIC_KEY = _read_secret("ALIPAY_PUBLIC_KEY")
ALIPAY_GATEWAY = os.getenv("ALIPAY_GATEWAY", "https://openapi-sandbox.dl.alipaydev.com/gateway.do")
ALIPAY_NOTIFY_URL = os.getenv("ALIPAY_NOTIFY_URL", "http://localhost:8000/api/payment/notify")
ALIPAY_RETURN_URL = os.getenv("ALIPAY_RETURN_URL", "http://localhost:5173/pay-result")

UPLOAD_DIR = BASE_DIR / "uploads"
