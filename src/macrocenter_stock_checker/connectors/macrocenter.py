"""Placeholder Macrocenter connector implementation."""

from __future__ import annotations

from typing import Any

from .base import BaseConnector


class MacrocenterConnector(BaseConnector):
    """Temporary placeholder connector for future Micro Center-specific logic."""

    source_name = "macrocenter"

    def fetch(self, product: dict[str, Any]) -> Any:
        """Fetch is intentionally unimplemented in foundation phase."""
        raise NotImplementedError("Phase 1 will implement MacrocenterConnector.fetch")

    def parse(self, raw_payload: Any) -> dict[str, Any]:
        """Parse is intentionally unimplemented in foundation phase."""
        raise NotImplementedError("Phase 1 will implement MacrocenterConnector.parse")
