from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


def database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:////data/stock_checker.db")


def sqlite_path_from_url(db_url: str) -> str:
    if not db_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in this MVP runtime")
    return db_url.replace("sqlite:///", "", 1)


@contextmanager
def connect():
    path = sqlite_path_from_url(database_url())
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS collector_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL,
            error_count INTEGER NOT NULL DEFAULT 0
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
        """
    )
