"""Connector protocol abstractions for source-specific implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Abstract connector contract for collecting product data from a source."""

    source_name: str

    @abstractmethod
    def fetch(self, product: dict[str, Any]) -> Any:
        """Fetch the raw source payload for a product descriptor."""

    @abstractmethod
    def parse(self, raw_payload: Any) -> dict[str, Any]:
        """Parse a raw payload into normalized snapshot fields."""
