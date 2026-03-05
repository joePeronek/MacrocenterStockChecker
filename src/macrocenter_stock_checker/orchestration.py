"""Helpers used by orchestration/runtime layers."""

from __future__ import annotations

from pathlib import Path

from .config import CatalogConfig, ProductConfig, load_catalog


def load_runtime_catalog(path: str | Path) -> CatalogConfig:
    """Load and validate catalog for runtime execution."""

    return load_catalog(path)


def resolve_products_for_run(catalog: CatalogConfig) -> list[ProductConfig]:
    """Return only active products whose stores are also active."""

    active_store_ids = {store.id for store in catalog.stores if store.active}
    return [
        product
        for product in catalog.products
        if product.active and product.source.store_id in active_store_ids
    ]
