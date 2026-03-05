"""CLI entrypoint for MacrocenterStockChecker."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the placeholder foundation commands."""
    parser = argparse.ArgumentParser(prog="macrocenter-stock-checker")
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the current package version.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the placeholder command-line interface."""
    from macrocenter_stock_checker import __version__

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
    else:
        print("MacrocenterStockChecker foundation is set up. Next step: implement check-now.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
