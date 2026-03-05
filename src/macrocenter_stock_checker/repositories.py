from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from .models import CollectorRun, Product, StockSnapshot
from .time_utils import utcnow


def upsert_product(
    session: Session,
    *,
    name: str,
    source: str,
    url: str,
    sku: str | None = None,
    active: bool = True,
) -> Product:
    existing = session.execute(
        select(Product).where(Product.source == source, Product.url == url)
    ).scalar_one_or_none()

    if existing:
        existing.name = name
        existing.sku = sku
        existing.active = active
        return existing

    product = Product(name=name, source=source, url=url, sku=sku, active=active)
    session.add(product)
    return product


def add_stock_snapshot(
    session: Session,
    *,
    product_id: int,
    in_stock: bool,
    stock_text: str | None,
    price: Decimal | None,
    currency: str | None,
    raw_payload: dict[str, Any] | None,
) -> StockSnapshot:
    snapshot = StockSnapshot(
        product_id=product_id,
        checked_at=utcnow(),
        in_stock=in_stock,
        stock_text=stock_text,
        price=price,
        currency=currency,
        raw_payload=raw_payload,
    )
    session.add(snapshot)
    return snapshot


def list_product_history(session: Session, product_id: int, *, limit: int = 100) -> Sequence[StockSnapshot]:
    stmt: Select[tuple[StockSnapshot]] = (
        select(StockSnapshot)
        .where(StockSnapshot.product_id == product_id)
        .order_by(StockSnapshot.checked_at.desc())
        .limit(limit)
    )
    return session.execute(stmt).scalars().all()


def create_collector_run(session: Session, *, status: str = "success", error_count: int = 0) -> CollectorRun:
    run = CollectorRun(started_at=utcnow(), status=status, error_count=error_count)
    session.add(run)
    return run
