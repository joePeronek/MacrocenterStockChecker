from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .collector import collect_snapshot
from .db import connect, init_db


def _seed_products(conn) -> list[tuple[int, str]]:
    products = conn.execute("SELECT id, name FROM products WHERE active = 1").fetchall()
    if products:
        return products

    conn.execute(
        "INSERT INTO products (name, sku, source, url, active) VALUES (?, ?, ?, ?, ?)",
        ("Demo Product", "DEMO-001", "macrocenter", "https://example.invalid/product/demo-001", 1),
    )
    return conn.execute("SELECT id, name FROM products WHERE active = 1").fetchall()


def check_now() -> int:
    with connect() as conn:
        init_db(conn)
        started = datetime.now(timezone.utc).isoformat()
        cur = conn.execute(
            "INSERT INTO collector_runs (started_at, status, error_count) VALUES (?, ?, ?)",
            (started, "running", 0),
        )
        run_id = cur.lastrowid

        for product_id, product_name in _seed_products(conn):
            snapshot = collect_snapshot(product_name)
            conn.execute(
                """
                INSERT INTO stock_snapshots
                (product_id, checked_at, in_stock, stock_text, price, currency, raw_payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    datetime.now(timezone.utc).isoformat(),
                    int(snapshot.in_stock),
                    snapshot.stock_text,
                    float(snapshot.price) if snapshot.price is not None else None,
                    snapshot.currency,
                    snapshot.raw_payload,
                ),
            )

        conn.execute(
            "UPDATE collector_runs SET status = ?, finished_at = ? WHERE id = ?",
            ("success", datetime.now(timezone.utc).isoformat(), run_id),
        )
    print("check-now completed")
    return 0


def healthcheck() -> int:
    with connect() as conn:
        init_db(conn)
        conn.execute("SELECT 1").fetchone()
    print("ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="macrocenter-checker")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check-now")
    subparsers.add_parser("healthcheck")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "check-now":
        return check_now()
    if args.command == "healthcheck":
        return healthcheck()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
