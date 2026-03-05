# MacrocenterStockChecker

Initial planning documentation is available in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md), including:
- Python vs C++ recommendation
- Proposed architecture
- MVP data model
- Phased implementation roadmap
- Docker-first considerations

## Config loader MVP

This repository now includes a typed config format for stores + products with validation:

- Example config: [`config/catalog.example.json`](config/catalog.example.json)
- Models + loader: [`src/macrocenter_stock_checker/config.py`](src/macrocenter_stock_checker/config.py)
- Runtime helpers: [`src/macrocenter_stock_checker/orchestration.py`](src/macrocenter_stock_checker/orchestration.py)

### Run tests

```bash
pytest
```
