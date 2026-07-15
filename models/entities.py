"""
SQLAlchemy ORM models (data entities).

These classes map 1:1 to SQLite tables. Controllers/views never import
SQLAlchemy sessions directly — they go through repositories/services.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class TimestampMixin:
    """Created / updated timestamps shared by mutable entities."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Category(Base, TimestampMixin):
    """Product category lookup table (extensible for reports later)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    products: Mapped[List["Product"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"


class Unit(Base, TimestampMixin):
    """Unit of measure lookup table (Piece, Kg, Litre, …)."""

    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    abbreviation: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    products: Mapped[List["Product"]] = relationship(back_populates="unit")

    def __repr__(self) -> str:
        return f"<Unit id={self.id} name={self.name!r}>"


class Vendor(Base, TimestampMixin):
    """Supplier / vendor master record."""

    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gst_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    products: Mapped[List["Product"]] = relationship(
        back_populates="vendor",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Vendor id={self.id} name={self.name!r}>"


class Product(Base, TimestampMixin):
    """Product supplied by a vendor (stock / pricing master)."""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("vendor_id", "sku", name="uq_vendor_sku"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    unit_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("units.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    company: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    sku: Mapped[Optional[str]] = mapped_column(String(80), nullable=True, index=True)
    batch_number: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    purchase_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    selling_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    mrp: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gst_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    stock_quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    minimum_stock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    manufacturing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    vendor: Mapped["Vendor"] = relationship(back_populates="products")
    category: Mapped[Optional["Category"]] = relationship(back_populates="products")
    unit: Mapped[Optional["Unit"]] = relationship(back_populates="products")

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} vendor_id={self.vendor_id}>"
