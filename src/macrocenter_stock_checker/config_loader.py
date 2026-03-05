from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ProductConfig(BaseModel):
    name: str
    source: str
    url: str
    sku: str | None = None
    active: bool = True


class CatalogConfig(BaseModel):
    products: list[ProductConfig] = Field(min_length=1)


def load_catalog(path: str | Path) -> CatalogConfig:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return CatalogConfig.model_validate(payload)
