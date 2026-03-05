"""Connector protocol abstractions for source-specific implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class ParsedSnapshot:
    """Normalized snapshot payload returned by connectors."""

    in_stock: bool
    stock_text: str | None
    price: Decimal | None
    currency: str | None
    raw_payload: dict[str, Any] | None


class BaseConnector(ABC):
    """Abstract connector contract for collecting product data from a source."""

    source_name: str

    @abstractmethod
    def fetch(self, product: dict[str, Any]) -> Any:
        """Fetch the raw source payload for a product descriptor."""

    @abstractmethod
    def parse(self, raw_payload: Any) -> ParsedSnapshot:
        """Parse a raw payload into normalized snapshot fields."""
