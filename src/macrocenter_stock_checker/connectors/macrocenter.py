"""Micro Center connector implementation."""

from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from bs4 import BeautifulSoup

from .base import BaseConnector, ParsedSnapshot

_PRICE_RE = re.compile(r"(\d+[\d,]*\.?\d*)")


class MacrocenterConnector(BaseConnector):
    """Connector for Micro Center product pages."""

    source_name = "macrocenter"

    def __init__(self, *, timeout_seconds: float = 10.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, product: dict[str, Any]) -> str:
        url = product.get("url")
        if not url:
            raise ValueError("product url is required for fetch")

        response = requests.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.text

    def parse(self, raw_payload: Any) -> ParsedSnapshot:
        html = str(raw_payload or "")
        if not html.strip():
            raise ValueError("empty payload")

        soup = BeautifulSoup(html, "html.parser")

        stock_text, stock_selector = self._extract_stock_text(soup)
        in_stock = self._interpret_stock(stock_text)

        price, currency, price_selector = self._extract_price_and_currency(soup)

        return ParsedSnapshot(
            in_stock=in_stock,
            stock_text=stock_text,
            price=price,
            currency=currency,
            raw_payload={
                "stock_selector": stock_selector,
                "price_selector": price_selector,
            },
        )

    def _extract_stock_text(self, soup: BeautifulSoup) -> tuple[str | None, str]:
        selectors = [
            "[data-testid='pdp-inventory-status']",
            ".inventory-status",
            "#inventory",
        ]
        for selector in selectors:
            tag = soup.select_one(selector)
            if tag and tag.get_text(strip=True):
                return tag.get_text(" ", strip=True), selector
        return None, "<none>"

    def _extract_price_and_currency(self, soup: BeautifulSoup) -> tuple[Decimal | None, str | None, str]:
        selectors = [
            "[data-testid='price']",
            ".product-price",
            "[itemprop='price']",
        ]
        for selector in selectors:
            tag = soup.select_one(selector)
            if not tag:
                continue
            text = tag.get_text(" ", strip=True)
            price = self._parse_price(text)
            if price is not None:
                return price, self._parse_currency(text) or self._meta_currency(soup), selector

        price, currency = self._json_ld_price(soup)
        return price, currency, "<none>"

    @staticmethod
    def _interpret_stock(stock_text: str | None) -> bool:
        if not stock_text:
            return False
        lowered = stock_text.lower()
        if "out of stock" in lowered or "sold out" in lowered or "unavailable" in lowered:
            return False
        return True

    @staticmethod
    def _parse_price(text: str | None) -> Decimal | None:
        if not text:
            return None
        match = _PRICE_RE.search(text.replace(",", ""))
        if not match:
            return None
        try:
            return Decimal(match.group(1))
        except InvalidOperation:
            return None

    @staticmethod
    def _meta_currency(soup: BeautifulSoup) -> str | None:
        node = soup.select_one("meta[property='product:price:currency']")
        if not node:
            return None
        content = node.get("content")
        return str(content).strip() if content else None

    @staticmethod
    def _parse_currency(text: str | None) -> str | None:
        if not text:
            return None
        upper = text.upper()
        for currency in ("USD", "RON", "EUR", "GBP"):
            if currency in upper:
                return currency
        return None

    def _json_ld_price(self, soup: BeautifulSoup) -> tuple[Decimal | None, str | None]:
        for tag in soup.select("script[type='application/ld+json']"):
            try:
                payload = json.loads(tag.get_text(strip=True))
            except json.JSONDecodeError:
                continue
            offers = payload.get("offers") if isinstance(payload, dict) else None
            if not isinstance(offers, dict):
                continue
            price = self._parse_price(str(offers.get("price")))
            currency = offers.get("priceCurrency")
            return price, str(currency) if currency else None
        return None, self._meta_currency(soup)
