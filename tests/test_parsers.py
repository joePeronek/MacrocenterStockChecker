from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from macrocenter_stock_checker.parsers import ParseError, parse_price_text, parse_stock_text

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "parser_cases.json"
_CASES = json.loads(_FIXTURE_PATH.read_text())


@pytest.mark.parametrize("case", _CASES["price"])
def test_parse_price_regression_cases(case: dict[str, str]) -> None:
    assert parse_price_text(case["raw"]) == Decimal(case["expected"])


@pytest.mark.parametrize("case", _CASES["stock"])
def test_parse_stock_regression_cases(case: dict[str, object]) -> None:
    assert parse_stock_text(str(case["raw"])) is bool(case["expected"])


@pytest.mark.parametrize("raw", _CASES["invalid_price"])
def test_parse_price_invalid_input(raw: str) -> None:
    with pytest.raises(ParseError):
        parse_price_text(raw)


@pytest.mark.parametrize("raw", _CASES["invalid_stock"])
def test_parse_stock_invalid_input(raw: str) -> None:
    with pytest.raises(ParseError):
        parse_stock_text(raw)
