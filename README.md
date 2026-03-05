# MacrocenterStockChecker

Python-first MVP for collecting stock + price snapshots and persisting historical runs.

## Quick start

1. Create virtualenv and install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Run checks:

```bash
ruff check .
ruff format --check .
pytest
```

3. Run a collection pass:

```bash
macrocenter-stock-checker check-now --config config/products.yaml --db-url sqlite+pysqlite:///macrocenter.db
```

## CLI

- `macrocenter-stock-checker --version`
- `macrocenter-stock-checker check-now --config <path> --db-url <sqlalchemy-url> --timeout 10`

`check-now` loads product config, fetches/parses pages, writes `products` and `stock_snapshots`, and records `collector_runs` status.
