from __future__ import annotations

import argparse
import logging
import sys

from . import db
from .config import load_products_config
from .workflow import RetrySettings, run_check_now


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def check_now(args: argparse.Namespace) -> int:
    configure_logging()
    conn = db.connect(args.db_path)
    db.ensure_schema(conn)

    if args.seed_products:
        products = load_products_config(args.seed_products)
        db.upsert_products(conn, products)

    result = run_check_now(
        conn,
        retry=RetrySettings(
            max_attempts=args.max_attempts,
            backoff_seconds=args.backoff_seconds,
            timeout_seconds=args.timeout_seconds,
        ),
    )
    print(
        f"run_id={result.run_id} status={result.status} "
        f"products={result.total_products} success={result.success_count} errors={result.error_count}"
    )

    if result.status == "success":
        return 0
    if result.status == "partial":
        return 2
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="macrocenter-stock-checker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check-now", help="Run one immediate stock collection")
    check_parser.add_argument("--db-path", default="stock_checker.db")
    check_parser.add_argument("--seed-products", help="JSON file with product definitions")
    check_parser.add_argument("--max-attempts", type=int, default=2)
    check_parser.add_argument("--backoff-seconds", type=float, default=0.2)
    check_parser.add_argument("--timeout-seconds", type=float, default=10.0)
    check_parser.set_defaults(func=check_now)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    rc = args.func(args)
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
