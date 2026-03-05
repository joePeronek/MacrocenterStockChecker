from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Product, Snapshot, utcnow_iso


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  sku TEXT,
  source TEXT NOT NULL,
  url TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS stock_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  checked_at TEXT NOT NULL,
  in_stock INTEGER NOT NULL,
  stock_text TEXT NOT NULL,
  price REAL,
  currency TEXT,
  raw_payload TEXT NOT NULL,
  FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS collector_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT,
  error_count INTEGER NOT NULL DEFAULT 0
);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def upsert_products(conn: sqlite3.Connection, products: list[dict]) -> None:
    for product in products:
        conn.execute(
            """
            INSERT INTO products(name, sku, source, url, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                product["name"],
                product.get("sku"),
                product["source"],
                product["url"],
                1 if product.get("active", True) else 0,
            ),
        )
    conn.commit()


def load_active_products(conn: sqlite3.Connection) -> list[Product]:
    rows = conn.execute(
        "SELECT id, name, source, url, sku, active FROM products WHERE active=1 ORDER BY id"
    ).fetchall()
    return [
        Product(
            id=row["id"],
            name=row["name"],
            source=row["source"],
            url=row["url"],
            sku=row["sku"],
            active=bool(row["active"]),
        )
        for row in rows
    ]


def start_run(conn: sqlite3.Connection) -> int:
    cur = conn.execute("INSERT INTO collector_runs(started_at) VALUES (?)", (utcnow_iso(),))
    conn.commit()
    return int(cur.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, status: str, error_count: int) -> None:
    conn.execute(
        """
        UPDATE collector_runs
        SET finished_at=?, status=?, error_count=?
        WHERE id=?
        """,
        (utcnow_iso(), status, error_count, run_id),
    )
    conn.commit()


def insert_snapshot(conn: sqlite3.Connection, product_id: int, snapshot: Snapshot) -> None:
    conn.execute(
        """
        INSERT INTO stock_snapshots(
            product_id, checked_at, in_stock, stock_text, price, currency, raw_payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_id,
            utcnow_iso(),
            1 if snapshot.in_stock else 0,
            snapshot.stock_text,
            snapshot.price,
            snapshot.currency,
            json.dumps(snapshot.raw_payload, separators=(",", ":")),
        ),
    )
    conn.commit()
