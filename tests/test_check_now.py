from __future__ import annotations

import json
from pathlib import Path

from macrocenter_stock_checker import db
from macrocenter_stock_checker.cli import build_parser
from macrocenter_stock_checker.models import Snapshot
from macrocenter_stock_checker.workflow import RetrySettings, run_check_now


class GoodConnector:
    def fetch_parse(self, product, timeout_seconds=10.0):
        return Snapshot(
            in_stock=True,
            stock_text="in stock",
            price=99.9,
            currency="RON",
            raw_payload={"ok": True, "id": product.id},
        )


class MixedConnector:
    def fetch_parse(self, product, timeout_seconds=10.0):
        if "bad" in product.name.lower():
            raise RuntimeError("boom")
        return Snapshot(
            in_stock=False,
            stock_text="out",
            price=None,
            currency=None,
            raw_payload={"ok": True},
        )


class BadConnector:
    def fetch_parse(self, product, timeout_seconds=10.0):
        raise TimeoutError("always fails")


def _seed(conn, products):
    db.ensure_schema(conn)
    db.upsert_products(conn, products)


def test_run_check_now_success(monkeypatch, tmp_path):
    from macrocenter_stock_checker import workflow

    monkeypatch.setitem(workflow.CONNECTOR_REGISTRY, "macrocenter", GoodConnector)

    conn = db.connect(tmp_path / "success.db")
    _seed(conn, [{"name": "P1", "source": "macrocenter", "url": "https://example.test/1"}])

    result = run_check_now(conn, retry=RetrySettings(max_attempts=1))

    assert result.status == "success"
    assert result.error_count == 0
    assert conn.execute("SELECT COUNT(*) FROM stock_snapshots").fetchone()[0] == 1


def test_run_check_now_partial(monkeypatch, tmp_path):
    from macrocenter_stock_checker import workflow

    monkeypatch.setitem(workflow.CONNECTOR_REGISTRY, "macrocenter", MixedConnector)

    conn = db.connect(tmp_path / "partial.db")
    _seed(
        conn,
        [
            {"name": "Good product", "source": "macrocenter", "url": "https://example.test/1"},
            {"name": "Bad product", "source": "macrocenter", "url": "https://example.test/2"},
        ],
    )

    result = run_check_now(conn, retry=RetrySettings(max_attempts=1))

    assert result.status == "partial"
    assert result.success_count == 1
    assert result.error_count == 1


def test_cli_exit_code_for_fail(monkeypatch, tmp_path):
    from macrocenter_stock_checker import workflow

    monkeypatch.setitem(workflow.CONNECTOR_REGISTRY, "macrocenter", BadConnector)

    products_file = tmp_path / "products.json"
    products_file.write_text(
        json.dumps([
            {"name": "Bad", "source": "macrocenter", "url": "https://example.test/bad"}
        ]),
        encoding="utf-8",
    )
    parser = build_parser()
    args = parser.parse_args(
        [
            "check-now",
            "--db-path",
            str(tmp_path / "cli.db"),
            "--seed-products",
            str(products_file),
            "--max-attempts",
            "1",
        ]
    )

    rc = args.func(args)
    assert rc == 1
