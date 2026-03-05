# MacrocenterStockChecker

Initial planning documentation is available in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Runtime (container-first)

This repository now includes a minimal Python runtime that supports a repeatable `check-now` execution inside Docker.

### Environment variables

- `DATABASE_URL` (default: `sqlite:////data/stock_checker.db`)
  - SQLite-first local runtime with a persistent Docker volume (`stock_checker_data`).

## Commands

### Build and run one collection now (SQLite default)

```bash
docker compose up --build app
```

This creates/uses `/data/stock_checker.db` inside the volume and executes one full run (`check-now`) that inserts a demo product snapshot.

### Run CLI locally (without Docker)

```bash
PYTHONPATH=src python -m macrocenter_stock_checker.cli check-now
PYTHONPATH=src python -m macrocenter_stock_checker.cli healthcheck
```

## Healthcheck strategy

- Image-level `HEALTHCHECK` calls `python -m macrocenter_stock_checker.cli healthcheck`.
- Compose service healthcheck mirrors the same command.
- `healthcheck` verifies table initialization and executes `SELECT 1` against the configured DB.

## Ops notes: SQLite-first now, PostgreSQL-later

- Current runtime is intentionally SQLite-first for zero-dependency local and container execution.
- Data persistence is provided through the named Docker volume `stock_checker_data`.
- To transition later to PostgreSQL:
  1. Introduce a DB abstraction layer (or ORM) for backend-agnostic SQL operations.
  2. Add migration tooling (for example Alembic) before switching production writes.
  3. Add a `postgres` compose profile with managed credentials via environment variables/secrets.
  4. Keep the `healthcheck` contract (`db connect + simple query`) unchanged so operational checks stay stable.
