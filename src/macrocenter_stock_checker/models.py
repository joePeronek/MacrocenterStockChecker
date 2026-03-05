from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class Product:
    id: int
    name: str
    source: str
    url: str
    sku: str | None = None
    active: bool = True


@dataclass(slots=True)
class Snapshot:
    in_stock: bool
    stock_text: str
    price: float | None
    currency: str | None
    raw_payload: dict


@dataclass(slots=True)
class CollectorRunResult:
    run_id: int
    status: str
    total_products: int
    success_count: int
    error_count: int


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
