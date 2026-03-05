from pathlib import Path
from decimal import Decimal

import pytest

from macrocenter_stock_checker.connectors import MacrocenterConnector


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "microcenter"


def _fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parse_in_stock_with_primary_selectors() -> None:
    connector = MacrocenterConnector()

    snapshot = connector.parse(_fixture("in_stock_primary.html"))

    assert snapshot.in_stock is True
    assert snapshot.stock_text == "In Stock at Cambridge"
    assert snapshot.price == Decimal("129.99")
    assert snapshot.currency == "USD"
    assert snapshot.raw_payload["stock_selector"] == "[data-testid='pdp-inventory-status']"
    assert snapshot.raw_payload["price_selector"] == "[data-testid='price']"


def test_parse_out_of_stock_with_fallback_selectors() -> None:
    connector = MacrocenterConnector()

    snapshot = connector.parse(_fixture("out_of_stock_fallback.html"))

    assert snapshot.in_stock is False
    assert snapshot.stock_text == "Sold Out - unavailable online"
    assert snapshot.price == Decimal("799.00")
    assert snapshot.currency is None
    assert snapshot.raw_payload["stock_selector"] == ".inventory-status"
    assert snapshot.raw_payload["price_selector"] == ".product-price"


def test_parse_uses_json_ld_fallback_for_price() -> None:
    connector = MacrocenterConnector()

    snapshot = connector.parse(_fixture("json_ld_price_only.html"))

    assert snapshot.in_stock is True
    assert snapshot.price == Decimal("19.95")
    assert snapshot.raw_payload["price_selector"] == "<none>"


def test_parse_rejects_empty_payload() -> None:
    connector = MacrocenterConnector()

    with pytest.raises(ValueError, match="empty payload"):
        connector.parse("   ")
