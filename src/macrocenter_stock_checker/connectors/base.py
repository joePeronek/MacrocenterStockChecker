"""Base connector contracts and normalized snapshot types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class ProductConfig:
    """Input data required for a connector lookup."""

    name: str
    url: str
    sku: str | None = None


@dataclass(frozen=True)
class Snapshot:
    """Store-independent normalized product snapshot."""

    in_stock: bool
    stock_text: str | None
    price: Decimal | None
    currency: str | None
    raw_payload: dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Adapter interface for store/source specific connectors."""

    @abstractmethod
    def fetch(self, product: ProductConfig) -> str:
        """Fetch raw source payload (typically HTML)."""

    @abstractmethod
    def parse(self, raw: str) -> Snapshot:
        """Parse a raw payload into a normalized Snapshot."""
