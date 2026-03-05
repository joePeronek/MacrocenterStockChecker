from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from .config_loader import CatalogConfig
from .connectors import MacrocenterConnector
from .repositories import (
    add_stock_snapshot,
    create_collector_run,
    upsert_product,
)
from .time_utils import utcnow

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RunResult:
    processed: int
    errors: int
    status: str


def run_check_now(session: Session, config: CatalogConfig, *, timeout_seconds: float = 10.0) -> RunResult:
    connector = MacrocenterConnector(timeout_seconds=timeout_seconds)
    run = create_collector_run(session, status="success", error_count=0)
    session.flush()

    processed = 0
    errors = 0

    for item in config.products:
        product = upsert_product(
            session,
            name=item.name,
            source=item.source,
            url=item.url,
            sku=item.sku,
            active=item.active,
        )
        session.flush()

        if not item.active:
            LOGGER.info("Skipping inactive product: %s", item.name)
            continue

        try:
            raw_payload = connector.fetch({"url": item.url, "name": item.name, "sku": item.sku})
            parsed = connector.parse(raw_payload)
            add_stock_snapshot(
                session,
                product_id=product.id,
                in_stock=parsed.in_stock,
                stock_text=parsed.stock_text,
                price=parsed.price,
                currency=parsed.currency,
                raw_payload=parsed.raw_payload,
            )
            processed += 1
            LOGGER.info("Collected %s (%s)", item.name, item.url)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            LOGGER.exception("Failed to collect %s: %s", item.url, exc)

    run.error_count = errors
    run.status = "fail" if processed == 0 and errors > 0 else "partial" if errors else "success"
    run.finished_at = utcnow()
    session.commit()

    return RunResult(processed=processed, errors=errors, status=run.status)
