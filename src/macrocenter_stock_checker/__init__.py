"""Core package for Macrocenter stock checker MVP."""

from .parsers import parse_price_text, parse_stock_text
from .retry import ErrorClass, classify_error, compute_backoff_seconds

__all__ = [
    "ErrorClass",
    "classify_error",
    "compute_backoff_seconds",
    "parse_price_text",
    "parse_stock_text",
]
