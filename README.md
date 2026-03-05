# MacrocenterStockChecker

Initial planning documentation is available in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md), including:
- Python vs C++ recommendation
- Proposed architecture
- MVP data model
- Phased implementation roadmap
- Docker-first considerations

## CLI MVP

This repository now includes a Python-first MVP CLI with a `check-now` command that:
- loads/optionally seeds configured products,
- fetches and parses one-source connector data,
- writes `stock_snapshots`, and
- records `collector_runs` with `success` / `partial` / `fail` status.

### Run locally

```bash
python -m macrocenter_stock_checker.cli check-now \
  --db-path stock_checker.db \
  --seed-products config/products.example.json
```

Exit codes:
- `0`: full success
- `2`: partial success (some products failed)
- `1`: full failure

### Product config format

`--seed-products` expects a JSON array:

```json
[
  {
    "name": "Example Product",
    "sku": "ABC-123",
    "source": "macrocenter",
    "url": "https://example.test/product.json",
    "active": true
  }
]
```

For the MVP connector, the URL response is expected to be JSON with keys like `in_stock`, `stock_text`, `price`, and `currency`.
