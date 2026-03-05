from pathlib import Path

import pytest

from macrocenter_stock_checker.config import ConfigError, load_catalog
from macrocenter_stock_checker.orchestration import resolve_products_for_run


ROOT = Path(__file__).resolve().parents[1]


def test_load_valid_catalog_example() -> None:
    catalog = load_catalog(ROOT / "config" / "catalog.example.json")

    assert catalog.version == 1
    assert len(catalog.stores) == 2
    assert len(catalog.products) == 3

    active_products = resolve_products_for_run(catalog)
    assert [product.id for product in active_products] == [
        "makita-drill-dhp482",
        "bosch-gws-750-angle-grinder",
    ]


def test_invalid_store_reference_fails_fast(tmp_path: Path) -> None:
    invalid_config = tmp_path / "invalid.json"
    invalid_config.write_text(
        """
{
  "version": 1,
  "stores": [
    {
      "id": "store-a",
      "name": "Store A",
      "kind": "macrocenter",
      "base_url": "https://example.com/"
    }
  ],
  "products": [
    {
      "id": "p1",
      "name": "Product 1",
      "source": {"store_id": "missing-store", "url": "https://example.com/p1"}
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError) as exc:
        load_catalog(invalid_config)

    assert "unknown store_id 'missing-store'" in str(exc.value)


def test_duplicate_product_ids_are_rejected(tmp_path: Path) -> None:
    invalid_config = tmp_path / "duplicate.json"
    invalid_config.write_text(
        """
{
  "version": 1,
  "stores": [
    {
      "id": "store-a",
      "name": "Store A",
      "kind": "macrocenter",
      "base_url": "https://example.com/"
    }
  ],
  "products": [
    {
      "id": "dup",
      "name": "Product 1",
      "source": {"store_id": "store-a", "url": "https://example.com/p1"}
    },
    {
      "id": "dup",
      "name": "Product 2",
      "source": {"store_id": "store-a", "url": "https://example.com/p2"}
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError) as exc:
        load_catalog(invalid_config)

    assert "Duplicate product id found: dup" in str(exc.value)
