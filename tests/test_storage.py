from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from macrocenter_stock_checker.database import init_db, make_session_factory
from macrocenter_stock_checker.models import Product
from macrocenter_stock_checker.repositories import add_stock_snapshot, list_product_history, upsert_product


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    init_db(engine)
    session_factory = make_session_factory(engine)
    with session_factory() as db_session:
        yield db_session


def test_upsert_product_creates_and_updates(session: Session) -> None:
    created = upsert_product(
        session,
        name="Test GPU",
        source="macrocenter",
        url="https://example.com/gpu",
        sku="GPU-1",
    )
    session.commit()

    assert created.id is not None

    updated = upsert_product(
        session,
        name="Test GPU Updated",
        source="macrocenter",
        url="https://example.com/gpu",
        sku="GPU-2",
        active=False,
    )
    session.commit()

    assert updated.id == created.id
    assert updated.name == "Test GPU Updated"
    assert updated.sku == "GPU-2"
    assert updated.active is False


def test_product_unique_constraint(session: Session) -> None:
    session.add(Product(name="A", source="macrocenter", url="https://example.com/a"))
    session.add(Product(name="B", source="macrocenter", url="https://example.com/a"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_snapshot_persistence_and_history(session: Session) -> None:
    product = upsert_product(
        session,
        name="Keyboard",
        source="macrocenter",
        url="https://example.com/keyboard",
    )
    session.flush()

    add_stock_snapshot(
        session,
        product_id=product.id,
        in_stock=True,
        stock_text="In stock (5)",
        price=Decimal("199.99"),
        currency="RON",
        raw_payload={"availability": "5", "price": "199.99"},
    )
    add_stock_snapshot(
        session,
        product_id=product.id,
        in_stock=False,
        stock_text="Out of stock",
        price=Decimal("199.99"),
        currency="RON",
        raw_payload={"availability": "0", "price": "199.99"},
    )
    session.commit()

    history = list_product_history(session, product.id)

    assert len(history) == 2
    assert history[0].stock_text == "Out of stock"
    assert history[1].stock_text == "In stock (5)"
    assert history[1].raw_payload == {"availability": "5", "price": "199.99"}
    assert history[1].checked_at.tzinfo is not None
