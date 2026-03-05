"""Micro Center connector implementation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re
from typing import Pattern
from urllib.request import Request, urlopen

from .base import BaseConnector, ProductConfig, Snapshot


@dataclass
class _SignalMatch:
    selector: str
    value: str | None


class MacrocenterConnector(BaseConnector):
    """Connector for collecting stock and price from Micro Center product pages."""

    STOCK_SELECTORS = (
        "[data-testid='pdp-inventory-status']",
        ".inventory-status",
        ".inventory",
        "#inventory",
    )
    PRICE_SELECTORS = (
        "[data-testid='price']",
        ".product-price",
        ".price",
        "meta[property='product:price:amount']",
    )

    _SELECTOR_PATTERNS: dict[str, Pattern[str]] = {
        "[data-testid='pdp-inventory-status']": re.compile(
            r"<(?P<tag>\w+)[^>]*data-testid=[\"']pdp-inventory-status[\"'][^>]*>(?P<text>.*?)</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        ),
        ".inventory": re.compile(
            r"<(?P<tag>\w+)[^>]*class=[\"'][^\"']*\binventory\b[^\"']*[\"'][^>]*>(?P<text>.*?)</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        ),
        ".inventory-status": re.compile(
            r"<(?P<tag>\w+)[^>]*class=[\"'][^\"']*\binventory-status\b[^\"']*[\"'][^>]*>(?P<text>.*?)</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        ),
        "#inventory": re.compile(
            r"<(?P<tag>\w+)[^>]*id=[\"']inventory[\"'][^>]*>(?P<text>.*?)</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        ),
        "[data-testid='price']": re.compile(
            r"<(?P<tag>\w+)[^>]*data-testid=[\"']price[\"'][^>]*>(?P<text>.*?)</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        ),
        ".price": re.compile(
            r"<(?P<tag>\w+)[^>]*class=[\"'][^\"']*\bprice\b[^\"']*[\"'][^>]*>(?P<text>.*?)</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        ),
        ".product-price": re.compile(
            r"<(?P<tag>\w+)[^>]*class=[\"'][^\"']*\bproduct-price\b[^\"']*[\"'][^>]*>(?P<text>.*?)</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        ),
        "meta[property='product:price:amount']": re.compile(
            r"<meta[^>]*property=[\"']product:price:amount[\"'][^>]*content=[\"'](?P<text>[^\"']+)[\"'][^>]*>",
            re.IGNORECASE | re.DOTALL,
        ),
    }

    _CURRENCY_META = re.compile(
        r"<meta[^>]*property=[\"']product:price:currency[\"'][^>]*content=[\"'](?P<value>[^\"']+)[\"'][^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    _JSON_LD_SCRIPT = re.compile(
        r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(?P<jsonld>.*?)</script>",
        re.IGNORECASE | re.DOTALL,
    )

    def __init__(self, timeout_s: float = 10.0, user_agent: str | None = None) -> None:
        self.timeout_s = timeout_s
        self.user_agent = user_agent or (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )

    def fetch(self, product: ProductConfig) -> str:
        request = Request(product.url, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=self.timeout_s) as response:  # noqa: S310
            return response.read().decode("utf-8", errors="replace")

    def parse(self, raw: str) -> Snapshot:
        if not raw or not raw.strip():
            raise ValueError("Micro Center parse failed: empty payload")

        stock_match = self._first_text_match(raw, self.STOCK_SELECTORS)
        price_match = self._first_text_match(raw, self.PRICE_SELECTORS)

        stock_text = self._clean_text(stock_match.value)
        in_stock = self._infer_in_stock(stock_text)

        price_raw = self._extract_price_value(raw, price_match)
        price, currency = self._parse_price_and_currency(price_raw, raw)

        return Snapshot(
            in_stock=in_stock,
            stock_text=stock_text,
            price=price,
            currency=currency,
            raw_payload={
                "stock_selector": stock_match.selector,
                "price_selector": price_match.selector,
                "stock_raw": stock_match.value,
                "price_raw": price_raw,
            },
        )

    def _first_text_match(self, raw: str, selectors: tuple[str, ...]) -> _SignalMatch:
        for selector in selectors:
            pattern = self._SELECTOR_PATTERNS[selector]
            match = pattern.search(raw)
            if not match:
                continue
            value = self._strip_tags(match.group("text"))
            if value:
                return _SignalMatch(selector=selector, value=value)
        return _SignalMatch(selector="<none>", value=None)

    def _extract_price_value(self, raw: str, price_match: _SignalMatch) -> str | None:
        if price_match.value:
            return price_match.value

        script_match = self._JSON_LD_SCRIPT.search(raw)
        if not script_match:
            return None

        payload = script_match.group("jsonld")
        marker = '"price"'
        if marker not in payload:
            return None

        _, _, tail = payload.partition(marker)
        _, _, value_side = tail.partition(":")
        candidate = value_side.split(",", 1)[0].splitlines()[0].strip()
        return candidate.strip('"{}[] ')

    def _parse_price_and_currency(self, raw_price: str | None, raw_html: str) -> tuple[Decimal | None, str | None]:
        if not raw_price:
            return None, None

        currency = "USD" if "$" in raw_price else None
        normalized = (
            raw_price.replace("$", "")
            .replace("USD", "")
            .replace(",", "")
            .strip()
        )

        try:
            price = Decimal(normalized)
        except InvalidOperation:
            return None, currency

        currency_meta = self._CURRENCY_META.search(raw_html)
        if currency_meta:
            currency = currency_meta.group("value")

        return price, currency

    def _infer_in_stock(self, stock_text: str | None) -> bool:
        if not stock_text:
            return False

        signal = stock_text.lower()
        if any(token in signal for token in ("out of stock", "sold out", "unavailable", "backorder")):
            return False
        if any(token in signal for token in ("in stock", "available", "pickup today", "limited availability")):
            return True
        return False

    def _clean_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        compact = " ".join(value.split())
        return compact or None

    def _strip_tags(self, html_fragment: str) -> str:
        return re.sub(r"<[^>]+>", " ", html_fragment)
