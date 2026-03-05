# Config directory

`products.yaml` defines product catalog entries consumed by `check-now`.

Each entry supports:
- `name` (required)
- `source` (required, currently `macrocenter`)
- `url` (required)
- `sku` (optional)
- `active` (optional, defaults to `true`)
