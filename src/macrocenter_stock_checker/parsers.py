"""Parser helpers for stock status and price normalization."""

from __future__ import annotations

import re
from decimal import Decimal

_PRICE_PATTERN = re.compile(r"(?P<value>\d{1,3}(?:[\s.,]\d{3})*(?:[.,]\d{2})|\d+[.,]\d{2}|\d+)")

_IN_STOCK_KEYWORDS = (
    "in stock",
    "available",
    "ready to ship",
    "na sklade",
    "disponibil",
)

_OUT_OF_STOCK_KEYWORDS = (
    "out of stock",
    "unavailable",
    "sold out",
    "stoc epuizat",
    "lipsa stoc",
)


class ParseError(ValueError):
    """Raised when parser receives invalid or non-normalizable input."""


def parse_price_text(raw_price: str) -> Decimal:
    """Extract and normalize price text into Decimal.

    Handles formats like: "1.999,99 RON", "1,999.99", "1999.99", "1 999,99".
    """
    if not raw_price or not raw_price.strip():
        raise ParseError("price text is empty")

    match = _PRICE_PATTERN.search(raw_price)
    if not match:
        raise ParseError(f"unable to parse price from '{raw_price}'")

    token = match.group("value").replace(" ", "")
    if "," in token and "." in token:
        last_dot = token.rfind(".")
        last_comma = token.rfind(",")
        if last_comma > last_dot:
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif "," in token:
        if token.count(",") > 1:
            token = token.replace(",", "")
        else:
            token = token.replace(",", ".")
    elif token.count(".") > 1:
        token = token.replace(".", "")

    try:
        return Decimal(token)
    except Exception as exc:  # noqa: BLE001
        raise ParseError(f"invalid normalized price '{token}'") from exc


def parse_stock_text(raw_stock: str) -> bool:
    """Classify stock strings to bool.

    True means in stock, False means out of stock.
    """
    if not raw_stock or not raw_stock.strip():
        raise ParseError("stock text is empty")

    normalized = raw_stock.strip().lower()
    if any(keyword in normalized for keyword in _OUT_OF_STOCK_KEYWORDS):
        return False
    if any(keyword in normalized for keyword in _IN_STOCK_KEYWORDS):
        return True

    raise ParseError(f"unknown stock status '{raw_stock}'")
