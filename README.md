# MacrocenterStockChecker

Initial planning documentation is available in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md), including:
- Python vs C++ recommendation
- Proposed architecture
- MVP data model
- Phased implementation roadmap
- Docker-first considerations

## MVP storage layer

This repository now includes a Python-first SQLAlchemy storage layer under `src/macrocenter_stock_checker`.

### Included schema
- `products`
- `stock_snapshots`
- `collector_runs`

### Initialization/migration approach (MVP)
For MVP, schema setup is handled via:

- `init_db(engine)` which runs `Base.metadata.create_all(...)`.

This is intentionally lightweight for SQLite-friendly local development. For production evolution, add Alembic migrations while preserving the same model definitions.

### Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```
