from __future__ import annotations

import json
from pathlib import Path


def load_products_config(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Products config must be a JSON list")
    return data
