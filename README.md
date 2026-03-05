# MacrocenterStockChecker

Initial planning documentation is available in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Implemented (Phase 1: Micro Center connector)

- Connector interface with normalized snapshot model in `src/macrocenter_stock_checker/connectors/base.py`.
- `MacrocenterConnector` implementation in `src/macrocenter_stock_checker/connectors/macrocenter.py` with:
  - `fetch(product)` using Python stdlib `urllib.request`
  - `parse(raw)` with fallback stock/price selector strategies
  - normalized fields: `in_stock`, `stock_text`, `price`, `currency`, and raw parser diagnostics
- Unit tests with local HTML fixtures in `tests/` (no network required).
- Parsing rules documentation in `docs/macrocenter_parser_rules.md`.

## Run tests

```bash
python -m pytest
```
