from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .time_utils import utcnow


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("source", "url", name="uq_products_source_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source: Mapped[str] = mapped_column(String(120), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    snapshots: Mapped[list[StockSnapshot]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class StockSnapshot(Base):
    __tablename__ = "stock_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False)
    stock_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    product: Mapped[Product] = relationship(back_populates="snapshots")


class CollectorRun(Base):
    __tablename__ = "collector_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
