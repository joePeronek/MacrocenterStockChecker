"""CLI entrypoint for MacrocenterStockChecker."""

from __future__ import annotations

import argparse
import logging

from .config_loader import load_catalog
from .database import create_engine_from_url, init_db, make_session_factory
from .workflow import run_check_now


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="macrocenter-stock-checker")
    parser.add_argument("--version", action="store_true", help="Print the current package version.")

    parser.add_argument("--db-url", default="sqlite+pysqlite:///macrocenter.db")

    subparsers = parser.add_subparsers(dest="command")
    check_now = subparsers.add_parser("check-now", help="Run an immediate collection pass")
    check_now.add_argument("--config", default="config/products.yaml")
    check_now.add_argument("--timeout", type=float, default=10.0)

    return parser


def main(argv: list[str] | None = None) -> int:
    from macrocenter_stock_checker import __version__

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    if args.command == "check-now":
        config = load_catalog(args.config)
        engine = create_engine_from_url(args.db_url)
        init_db(engine)
        session_factory = make_session_factory(engine)
        with session_factory() as session:
            result = run_check_now(session, config, timeout_seconds=args.timeout)
        print(
            f"check-now complete: status={result.status} processed={result.processed} errors={result.errors}"
        )
        return 0 if result.status in {"success", "partial"} else 1

    print("MacrocenterStockChecker foundation is set up. Use 'check-now' to run collection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
