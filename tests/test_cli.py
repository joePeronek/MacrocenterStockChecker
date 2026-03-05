from __future__ import annotations

import sqlite3
from pathlib import Path

from macrocenter_stock_checker.cli import check_now, healthcheck


def test_check_now_writes_snapshot(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    assert check_now() == 0

    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) FROM stock_snapshots").fetchone()[0]
    finally:
        conn.close()

    assert count == 1


def test_healthcheck_passes(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "health.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    assert healthcheck() == 0
