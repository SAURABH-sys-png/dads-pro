"""
Plain data-transfer objects used between services and views.

Views never receive live SQLAlchemy instances — this avoids detached-session
bugs and keeps the UI layer independent of the ORM.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Dict, Optional


@dataclass
class VendorDTO:
    """Vendor row ready for list / form / details screens."""

    id: Optional[int] = None
    name: str = ""
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    gst_number: str = ""
    remarks: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    products_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProductDTO:
    """Product row ready for Excel-like tables and forms."""

    id: Optional[int] = None
    vendor_id: int = 0
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    name: str = ""
    company: str = ""
    sku: str = ""
    batch_number: str = ""
    purchase_price: float = 0.0
    selling_price: float = 0.0
    mrp: float = 0.0
    gst_percent: float = 0.0
    stock_quantity: float = 0.0
    minimum_stock: float = 0.0
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    remarks: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Joined display fields
    category_name: str = ""
    unit_name: str = ""
    vendor_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LookupDTO:
    """Simple id/name pair for combo boxes (categories, units)."""

    id: int
    name: str
    extra: Dict[str, Any] = field(default_factory=dict)
