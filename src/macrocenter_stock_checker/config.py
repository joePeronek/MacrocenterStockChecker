"""Config models and loader for product catalog definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class ConfigError(ValueError):
    """Raised when configuration files are invalid or unreadable."""


@dataclass(slots=True)
class StoreConfig:
    id: str
    name: str
    kind: str
    base_url: str
    active: bool = True
    timeout_seconds: int = 15
    headers: dict[str, str] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProductSource:
    store_id: str
    url: str
    sku: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProductConfig:
    id: str
    name: str
    source: ProductSource
    active: bool = True


@dataclass(slots=True)
class CatalogConfig:
    version: int
    stores: list[StoreConfig]
    products: list[ProductConfig]


SUPPORTED_CONFIG_EXTENSIONS = {".json"}


def _expect_dict(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{path} must be an object")
    return value


def _expect_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ConfigError(f"{path} must be a list")
    return value


def _expect_str(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{path} must be a non-empty string")
    return value


def _expect_bool(value: Any, path: str, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ConfigError(f"{path} must be a boolean")
    return value


def _expect_int(value: Any, path: str, default: int, minimum: int, maximum: int) -> int:
    if value is None:
        return default
    if not isinstance(value, int):
        raise ConfigError(f"{path} must be an integer")
    if value < minimum or value > maximum:
        raise ConfigError(f"{path} must be between {minimum} and {maximum}")
    return value


def _expect_url(value: Any, path: str) -> str:
    url = _expect_str(value, path)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigError(f"{path} must be a valid http(s) URL")
    return url


def _expect_str_dict(value: Any, path: str) -> dict[str, str]:
    if value is None:
        return {}
    obj = _expect_dict(value, path)
    for key, item in obj.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise ConfigError(f"{path} must be a string-to-string map")
    return obj


def _expect_any_dict(value: Any, path: str) -> dict[str, Any]:
    if value is None:
        return {}
    return _expect_dict(value, path)


def _parse_store(raw: Any, index: int) -> StoreConfig:
    path = f"stores[{index}]"
    data = _expect_dict(raw, path)
    return StoreConfig(
        id=_expect_str(data.get("id"), f"{path}.id"),
        name=_expect_str(data.get("name"), f"{path}.name"),
        kind=_expect_str(data.get("kind"), f"{path}.kind"),
        base_url=_expect_url(data.get("base_url"), f"{path}.base_url"),
        active=_expect_bool(data.get("active"), f"{path}.active", default=True),
        timeout_seconds=_expect_int(
            data.get("timeout_seconds"),
            f"{path}.timeout_seconds",
            default=15,
            minimum=1,
            maximum=120,
        ),
        headers=_expect_str_dict(data.get("headers"), f"{path}.headers"),
        settings=_expect_any_dict(data.get("settings"), f"{path}.settings"),
    )


def _parse_source(raw: Any, path: str) -> ProductSource:
    data = _expect_dict(raw, path)
    sku = data.get("sku")
    if sku is not None and not isinstance(sku, str):
        raise ConfigError(f"{path}.sku must be a string when provided")
    return ProductSource(
        store_id=_expect_str(data.get("store_id"), f"{path}.store_id"),
        url=_expect_url(data.get("url"), f"{path}.url"),
        sku=sku,
        metadata=_expect_any_dict(data.get("metadata"), f"{path}.metadata"),
    )


def _parse_product(raw: Any, index: int) -> ProductConfig:
    path = f"products[{index}]"
    data = _expect_dict(raw, path)
    return ProductConfig(
        id=_expect_str(data.get("id"), f"{path}.id"),
        name=_expect_str(data.get("name"), f"{path}.name"),
        active=_expect_bool(data.get("active"), f"{path}.active", default=True),
        source=_parse_source(data.get("source"), f"{path}.source"),
    )


def _validate_relationships(stores: list[StoreConfig], products: list[ProductConfig]) -> None:
    store_ids: set[str] = set()
    for store in stores:
        if store.id in store_ids:
            raise ConfigError(f"Duplicate store id found: {store.id}")
        store_ids.add(store.id)

    product_ids: set[str] = set()
    for product in products:
        if product.id in product_ids:
            raise ConfigError(f"Duplicate product id found: {product.id}")
        product_ids.add(product.id)

        if product.source.store_id not in store_ids:
            raise ConfigError(
                f"Product '{product.id}' references unknown store_id '{product.source.store_id}'. "
                "Ensure the store exists in 'stores'."
            )

    stores_by_id = {store.id: store for store in stores}
    for product in products:
        if product.active and not stores_by_id[product.source.store_id].active:
            raise ConfigError(
                f"Product '{product.id}' is active but its store '{product.source.store_id}' is inactive. "
                "Either disable the product or activate the store."
            )


def load_catalog(path: str | Path) -> CatalogConfig:
    """Load and validate a catalog config file."""

    config_path = Path(path)
    if config_path.suffix.lower() not in SUPPORTED_CONFIG_EXTENSIONS:
        raise ConfigError(
            f"Unsupported config extension '{config_path.suffix}'. Supported: .json"
        )

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"Failed to read config file '{config_path}': {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Failed to parse config file '{config_path}': {exc}") from exc

    root = _expect_dict(payload, "root")
    version = _expect_int(root.get("version"), "version", default=1, minimum=1, maximum=1000)
    stores = [_parse_store(item, idx) for idx, item in enumerate(_expect_list(root.get("stores", []), "stores"))]
    products = [
        _parse_product(item, idx)
        for idx, item in enumerate(_expect_list(root.get("products", []), "products"))
    ]

    _validate_relationships(stores, products)
    return CatalogConfig(version=version, stores=stores, products=products)
