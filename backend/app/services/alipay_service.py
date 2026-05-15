import json

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.util.SignatureUtils import verify_with_rsa

from app.config import (
    ALIPAY_APPID,
    ALIPAY_PRIVATE_KEY,
    ALIPAY_PUBLIC_KEY,
    ALIPAY_GATEWAY,
    ALIPAY_NOTIFY_URL,
    ALIPAY_RETURN_URL,
)


def _build_client() -> DefaultAlipayClient:
    config = AlipayClientConfig()
    config.server_url = ALIPAY_GATEWAY
    config.app_id = ALIPAY_APPID
    config.app_private_key = ALIPAY_PRIVATE_KEY
    config.alipay_public_key = ALIPAY_PUBLIC_KEY
    config.sign_type = "RSA2"
    config.format = "json"
    config.charset = "utf-8"
    return DefaultAlipayClient(alipay_client_config=config)


def create_page_pay_url(order_no: str, total_amount: int, subject: str) -> str:
    """Generate Alipay page pay URL (PC web). total_amount in cents."""
    model = AlipayTradePagePayModel()
    model.out_trade_no = order_no
    model.total_amount = f"{total_amount / 100:.2f}"
    model.subject = subject
    model.product_code = "FAST_INSTANT_TRADE_PAY"

    request = AlipayTradePagePayRequest(biz_model=model)
    request.notify_url = ALIPAY_NOTIFY_URL
    request.return_url = ALIPAY_RETURN_URL

    client = _build_client()
    return client.page_execute(request, http_method="GET")


def verify_notify(data: dict) -> bool:
    """Verify async notify signature from Alipay."""
    sign = data.pop("sign", None)
    if not sign:
        return False
    sign_type = data.pop("sign_type", "RSA2")
    content = "&".join(f"{k}={v}" for k, v in sorted(data.items()) if v)
    return verify_with_rsa(ALIPAY_PUBLIC_KEY, content, sign, sign_type)


def query_payment(out_trade_no: str) -> dict | None:
    """Query payment status from Alipay."""
    model = AlipayTradeQueryModel()
    model.out_trade_no = out_trade_no

    request = AlipayTradeQueryRequest(biz_model=model)

    client = _build_client()
    try:
        response = client.execute(request)
        return json.loads(response)
    except Exception:
        return None
