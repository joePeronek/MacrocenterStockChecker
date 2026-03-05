from __future__ import annotations

from macrocenter_stock_checker.retry import ErrorClass, classify_error, compute_backoff_seconds


class TimeoutErrorLike(Exception):
    pass


class ConnectionErrorLike(Exception):
    pass


def test_classify_error_from_status_codes() -> None:
    assert classify_error(Exception(""), status_code=429) is ErrorClass.THROTTLED
    assert classify_error(Exception(""), status_code=503) is ErrorClass.TRANSIENT
    assert classify_error(Exception(""), status_code=404) is ErrorClass.PERMANENT


def test_classify_error_from_exception_name_and_message() -> None:
    assert classify_error(TimeoutErrorLike("request timeout")) is ErrorClass.TRANSIENT
    assert classify_error(ConnectionErrorLike("socket reset")) is ErrorClass.TRANSIENT
    assert classify_error(Exception("rate limit reached")) is ErrorClass.THROTTLED


def test_compute_backoff_seconds_is_deterministic() -> None:
    assert compute_backoff_seconds(1, ErrorClass.TRANSIENT) == 1.0
    assert compute_backoff_seconds(3, ErrorClass.TRANSIENT) == 4.0
    assert compute_backoff_seconds(1, ErrorClass.THROTTLED) == 2.0
    assert compute_backoff_seconds(3, ErrorClass.THROTTLED) == 8.0
    assert compute_backoff_seconds(2, ErrorClass.PERMANENT) == 0.0
