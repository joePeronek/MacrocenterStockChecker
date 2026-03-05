# MacrocenterStockChecker

Python-first MVP for collecting stock + price snapshots and persisting historical runs.

## Current status

Phase 0 foundation is complete:
- Python package skeleton under `src/`
- Connector module layout for future store implementations
- Basic CLI entrypoint
- Test + lint tooling wired with `pytest` and `ruff`
- Reserved `config/` directory for runtime configuration

See the roadmap in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Project layout

```text
.
├── config/
├── src/
│   └── macrocenter_stock_checker/
│       ├── cli.py
│       └── connectors/
└── tests/
```

## Local development

### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install the package with dev dependencies

```bash
pip install -e ".[dev]"
```

### 3) Run the placeholder CLI

```bash
macrocenter-stock-checker
macrocenter-stock-checker --version
```

## Tooling commands

### Format/lint

```bash
ruff format .
ruff check .
```

### Tests

```bash
pytest
```

## Notes

- The current CLI is intentionally minimal and confirms environment wiring.
- Full collection flow (`check-now`) and connector parsing behavior are planned for later phases.
