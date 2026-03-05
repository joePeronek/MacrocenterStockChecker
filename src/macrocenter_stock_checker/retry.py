"""Retry and error classification helpers for collector reliability."""

from __future__ import annotations

from enum import Enum


class ErrorClass(str, Enum):
    TRANSIENT = "transient"
    THROTTLED = "throttled"
    PERMANENT = "permanent"


def classify_error(error: Exception, status_code: int | None = None) -> ErrorClass:
    """Classify exceptions/status codes into retry policy buckets."""
    name = error.__class__.__name__.lower()
    message = str(error).lower()

    if status_code == 429:
        return ErrorClass.THROTTLED
    if status_code and 500 <= status_code <= 599:
        return ErrorClass.TRANSIENT
    if status_code and 400 <= status_code <= 499:
        return ErrorClass.PERMANENT

    if "timeout" in name or "timeout" in message:
        return ErrorClass.TRANSIENT
    if "connection" in name or "network" in message:
        return ErrorClass.TRANSIENT
    if "rate" in message and "limit" in message:
        return ErrorClass.THROTTLED

    return ErrorClass.PERMANENT


def compute_backoff_seconds(attempt: int, error_class: ErrorClass) -> float:
    """Return deterministic backoff for given attempt and error class."""
    base = 1.0 if error_class is ErrorClass.TRANSIENT else 2.0
    if error_class is ErrorClass.PERMANENT:
        return 0.0
    attempt = max(1, attempt)
    return base * (2 ** (attempt - 1))
