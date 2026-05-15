import uuid
from datetime import datetime, timezone


def generate_order_no() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:8].upper()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
