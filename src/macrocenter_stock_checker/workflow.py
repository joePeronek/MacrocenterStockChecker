from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from . import db
from .connectors import CONNECTOR_REGISTRY
from .models import CollectorRunResult, Product


LOGGER = logging.getLogger("macrocenter_stock_checker")


@dataclass(slots=True)
class RetrySettings:
    max_attempts: int = 2
    backoff_seconds: float = 0.2
    timeout_seconds: float = 10.0


def _collect_product(product: Product, retry: RetrySettings) -> tuple[bool, Exception | None]:
    connector_cls = CONNECTOR_REGISTRY.get(product.source)
    if connector_cls is None:
        return False, ValueError(f"Unsupported source: {product.source}")

    connector = connector_cls()
    last_error: Exception | None = None
    for attempt in range(1, retry.max_attempts + 1):
        try:
            snapshot = connector.fetch_parse(product, timeout_seconds=retry.timeout_seconds)
            return True, snapshot
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            LOGGER.warning(
                "product_collect_attempt_failed",
                extra={
                    "product_id": product.id,
                    "product": product.name,
                    "attempt": attempt,
                    "max_attempts": retry.max_attempts,
                    "error": str(exc),
                },
            )
            if attempt < retry.max_attempts:
                time.sleep(retry.backoff_seconds)

    return False, last_error


def run_check_now(conn, retry: RetrySettings | None = None) -> CollectorRunResult:
    retry = retry or RetrySettings()
    run_id = db.start_run(conn)
    products = db.load_active_products(conn)
    success_count = 0
    error_count = 0

    for product in products:
        ok, result = _collect_product(product, retry)
        if ok:
            db.insert_snapshot(conn, product.id, result)
            success_count += 1
            LOGGER.info(
                "product_collected",
                extra={"run_id": run_id, "product_id": product.id, "product": product.name},
            )
        else:
            error_count += 1
            LOGGER.error(
                "product_collect_failed",
                extra={
                    "run_id": run_id,
                    "product_id": product.id,
                    "product": product.name,
                    "error": str(result),
                },
            )

    if not products or error_count == 0:
        status = "success"
    elif success_count == 0:
        status = "fail"
    else:
        status = "partial"

    db.finish_run(conn, run_id, status, error_count)
    return CollectorRunResult(
        run_id=run_id,
        status=status,
        total_products=len(products),
        success_count=success_count,
        error_count=error_count,
    )
