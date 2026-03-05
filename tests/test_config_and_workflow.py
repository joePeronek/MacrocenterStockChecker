from __future__ import annotations

from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from macrocenter_stock_checker.config_loader import load_catalog
from macrocenter_stock_checker.connectors import ParsedSnapshot
from macrocenter_stock_checker.database import init_db, make_session_factory
from macrocenter_stock_checker.models import CollectorRun, Product, StockSnapshot
from macrocenter_stock_checker.workflow import run_check_now


def test_load_catalog_parses_products(tmp_path) -> None:
    config_file = tmp_path / "products.yaml"
    config_file.write_text(
        """
products:
  - name: Test Product
    source: macrocenter
    url: https://example.com/item
""".strip(),
        encoding="utf-8",
    )

    catalog = load_catalog(config_file)

    assert len(catalog.products) == 1
    assert catalog.products[0].active is True


def test_run_check_now_persists_run_and_snapshot(monkeypatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    init_db(engine)
    session_factory = make_session_factory(engine)

    def fake_fetch(self, product):
        return "<html><div data-testid='pdp-inventory-status'>In Stock</div><div data-testid='price'>$12.34</div></html>"

    monkeypatch.setattr("macrocenter_stock_checker.connectors.macrocenter.MacrocenterConnector.fetch", fake_fetch)

    class DummyConfig:
        products = [
            type("P", (), {"name": "A", "source": "macrocenter", "url": "https://e", "sku": None, "active": True})()
        ]

    with session_factory() as session:
        result = run_check_now(session, DummyConfig())

    assert result.status == "success"

    with Session(engine) as check_session:
        runs = check_session.scalars(select(CollectorRun)).all()
        products = check_session.scalars(select(Product)).all()
        snapshots = check_session.scalars(select(StockSnapshot)).all()

    assert len(runs) == 1
    assert len(products) == 1
    assert len(snapshots) == 1
    assert snapshots[0].price == Decimal("12.34")


def test_parsed_snapshot_dataclass_smoke() -> None:
    snapshot = ParsedSnapshot(
        in_stock=True,
        stock_text="In Stock",
        price=Decimal("1.00"),
        currency="USD",
        raw_payload={},
    )

    assert snapshot.in_stock is True
