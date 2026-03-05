from __future__ import annotations

import json
from urllib.request import Request, urlopen

from .models import Product, Snapshot


class BaseConnector:
    def fetch_parse(self, product: Product, timeout_seconds: float = 10.0) -> Snapshot:
        raise NotImplementedError


class MacrocenterConnector(BaseConnector):
    """MVP connector expecting a JSON payload at the product URL."""

    def fetch_parse(self, product: Product, timeout_seconds: float = 10.0) -> Snapshot:
        req = Request(product.url, headers={"User-Agent": "MacrocenterStockChecker/0.1"})
        with urlopen(req, timeout=timeout_seconds) as resp:  # nosec B310 - controlled via config
            payload = json.loads(resp.read().decode("utf-8"))
        return Snapshot(
            in_stock=bool(payload.get("in_stock", False)),
            stock_text=str(payload.get("stock_text", "unknown")),
            price=float(payload["price"]) if payload.get("price") is not None else None,
            currency=payload.get("currency"),
            raw_payload=payload,
        )


CONNECTOR_REGISTRY = {
    "macrocenter": MacrocenterConnector,
}
