from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal


@dataclass
class CollectedSnapshot:
    in_stock: bool
    stock_text: str
    price: Decimal | None
    currency: str | None
    raw_payload: str


def collect_snapshot(product_name: str) -> CollectedSnapshot:
    """Deterministic collector placeholder for container/runtime bring-up."""
    payload = {
        "product": product_name,
        "status": "in_stock",
        "price": "99.99",
        "currency": "RON",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }
    return CollectedSnapshot(
        in_stock=True,
        stock_text="In stock",
        price=Decimal("99.99"),
        currency="RON",
        raw_payload=json.dumps(payload),
    )
