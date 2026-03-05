# Stock Checker & Tracker Implementation Plan

## 1) Goal and Scope
Build a container-friendly application that:
- Monitors stock availability for many products across one or more stores/sites.
- Tracks current price and historical price/stock changes over time.
- Stores normalized data so summaries, alerts, and dashboards can be added later.

Initial delivery focus: **data collection + storage + repeatable runs** (summarization deferred).

---

## 2) Language Choice: Python vs C++

### Recommended first implementation: Python
Python is the better starting point for this project because it provides:
- Faster development for HTTP/API clients, scraping, scheduling, and data pipelines.
- Strong libraries (`httpx`, `beautifulsoup4`, `playwright`, `pydantic`, `sqlalchemy`, `pandas`).
- Easier iteration when target websites change.
- Simpler containerization and CI setup.

### Where C++ can fit later
C++ can be introduced later for:
- High-performance parsing modules.
- CPU-intensive analytics.
- Native binaries for constrained environments.

### Decision
Start with **Python** now; keep architecture modular so components can be replaced by C++ services if needed.

---

## 3) High-Level Architecture

1. **Config Layer**
   - Product catalog (URLs/SKUs/selectors).
   - Source/store settings.
   - Runtime options (frequency, retries, timeouts).

2. **Collector Layer**
   - One connector per store/source.
   - Fetch product pages or APIs.
   - Parse stock + price.

3. **Normalizer Layer**
   - Convert source-specific data into a unified schema.
   - Add timestamp, currency, availability status.

4. **Storage Layer**
   - Persist snapshots in SQL database.
   - Preserve full history to enable trends.

5. **Orchestration Layer**
   - Run checks on schedule (cron/worker loop).
   - Handle retries/backoff and error reporting.

6. **Output Layer (later)**
   - Summary reports, alerts, and dashboards.

---

## 4) Proposed Tech Stack (Python)

- **Runtime**: Python 3.12+
- **HTTP**: `httpx`
- **Parsing**: `beautifulsoup4`, `lxml`
- **Dynamic pages (if needed)**: `playwright`
- **Data models/validation**: `pydantic`
- **Database ORM**: `sqlalchemy`
- **Database**:
  - Start: SQLite (simple local/dev)
  - Production: PostgreSQL
- **Scheduling**:
  - Start: simple interval runner or cron in container
  - Later: APScheduler/Celery if needed
- **Logging**: `structlog` or stdlib logging (JSON format)
- **Packaging**: Docker + `docker-compose`

---

## 5) Data Model (MVP)

### `products`
- `id`
- `name`
- `sku` (optional)
- `source`
- `url`
- `active`

### `stock_snapshots`
- `id`
- `product_id`
- `checked_at` (UTC)
- `in_stock` (bool)
- `stock_text` (raw source string)
- `price`
- `currency`
- `raw_payload` (JSON blob for debugging)

### `collector_runs`
- `id`
- `started_at`
- `finished_at`
- `status` (success/partial/fail)
- `error_count`

This supports both point-in-time checks and historical trends.

---

## 6) Implementation Phases

## Phase 0: Foundation
- Initialize project skeleton (`src/`, `tests/`, `config/`).
- Add Python tooling: `pyproject.toml`, formatter/linter (`ruff`), tests (`pytest`).
- Add Dockerfile and compose file.

### Phase 1: Core MVP
- Define product config format (YAML/JSON).
- Build one source connector end-to-end.
- Parse stock + price and save snapshots.
- Add CLI command: `check-now`.

### Phase 2: Multi-product + Scheduling
- Batch check multiple products.
- Add robust retry + timeout + rate-limit behavior.
- Add recurring run mode (loop/cron).

### Phase 3: Reliability
- Structured logging + per-product error capture.
- Health endpoint or status command.
- Basic metrics (items checked, failures, avg duration).

### Phase 4: Extensibility
- Add connector interface for new stores.
- Add integration tests with mocked responses.
- Prepare hooks for summary/alert modules.

---

## 7) Connector Strategy

Use an adapter pattern:
- `BaseConnector` interface:
  - `fetch(product) -> raw_response`
  - `parse(raw_response) -> NormalizedSnapshot`
- `MacrocenterConnector`, `OtherStoreConnector`, etc.

Benefits:
- Isolate per-site HTML/API changes.
- Keep core pipeline stable.
- Easier testing and maintenance.

---

## 8) Docker-First Considerations

- Keep app stateless except database volume.
- Use env vars for configuration and secrets.
- Set explicit timezone handling (store UTC in DB).
- Run as non-root user in container.
- Add healthcheck to validate DB connectivity.

---

## 9) Risks and Mitigations

1. **Website layout changes**
   - Mitigation: connector isolation + parser tests + fallback selectors.

2. **Anti-bot/rate limiting**
   - Mitigation: request pacing, retries with backoff, user-agent strategy.

3. **Dynamic JS-heavy pages**
   - Mitigation: default to HTTP parsing; use Playwright only when required.

4. **Data quality inconsistency**
   - Mitigation: strict validation in normalizer + store raw payload for audits.

---

## 10) Suggested Next Action Items

1. Confirm language choice (**Python recommended**).
2. List first 5-10 target products + sources.
3. Decide initial database target (SQLite vs PostgreSQL).
4. Implement Phase 0 + Phase 1 for one connector.
5. Add scheduled run in Docker and inspect collected history.

---

## 11) If You Prefer C++

A viable C++ path is possible, but development will be slower initially. Equivalent stack might include:
- HTTP: `cpr` or `Boost.Beast`
- HTML parsing: `gumbo-parser`/`lexbor`
- JSON: `nlohmann/json`
- DB: `libpqxx` (PostgreSQL) / SQLite C API
- Scheduling: external cron + executable

Recommended compromise:
- Use Python for collector/orchestration now.
- Add C++ microservice later for high-performance analytics if needed.
