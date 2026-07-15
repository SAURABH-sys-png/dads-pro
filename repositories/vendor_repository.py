"""
Vendor repository — all SQL for the vendors table lives here.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from models.dto import VendorDTO
from models.entities import Product, Vendor
from repositories.base import BaseRepository


def _to_dto(vendor: Vendor, products_count: int = 0) -> VendorDTO:
    return VendorDTO(
        id=vendor.id,
        name=vendor.name or "",
        contact_person=vendor.contact_person or "",
        phone=vendor.phone or "",
        email=vendor.email or "",
        address=vendor.address or "",
        gst_number=vendor.gst_number or "",
        remarks=vendor.remarks or "",
        is_active=bool(vendor.is_active),
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
        products_count=products_count,
    )


class VendorRepository(BaseRepository[Vendor]):
    """Data-access API for vendors."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Vendor)

    def list_all(self, search: str = "") -> List[VendorDTO]:
        """Return vendors with product counts, optionally filtered by search."""
        count_subq = (
            select(Product.vendor_id, func.count(Product.id).label("cnt"))
            .where(Product.is_active.is_(True))
            .group_by(Product.vendor_id)
            .subquery()
        )

        stmt = (
            select(Vendor, func.coalesce(count_subq.c.cnt, 0))
            .outerjoin(count_subq, Vendor.id == count_subq.c.vendor_id)
            .where(Vendor.is_active.is_(True))
            .order_by(Vendor.name.asc())
        )

        term = search.strip()
        if term:
            like = f"%{term}%"
            stmt = stmt.where(
                or_(
                    Vendor.name.ilike(like),
                    Vendor.phone.ilike(like),
                    Vendor.gst_number.ilike(like),
                    Vendor.contact_person.ilike(like),
                    Vendor.email.ilike(like),
                )
            )

        rows = self.session.execute(stmt).all()
        return [_to_dto(vendor, int(count)) for vendor, count in rows]

    def get_dto(self, vendor_id: int) -> Optional[VendorDTO]:
        vendor = self.get_by_id(vendor_id)
        if vendor is None or not vendor.is_active:
            return None
        count = self.session.scalar(
            select(func.count(Product.id)).where(
                Product.vendor_id == vendor_id,
                Product.is_active.is_(True),
            )
        )
        return _to_dto(vendor, int(count or 0))

    def create(self, data: VendorDTO) -> VendorDTO:
        vendor = Vendor(
            name=data.name.strip(),
            contact_person=data.contact_person.strip() or None,
            phone=data.phone.strip() or None,
            email=data.email.strip() or None,
            address=data.address.strip() or None,
            gst_number=data.gst_number.strip() or None,
            remarks=data.remarks.strip() or None,
            is_active=True,
        )
        self.add(vendor)
        return _to_dto(vendor, 0)

    def update(self, vendor_id: int, data: VendorDTO) -> Optional[VendorDTO]:
        vendor = self.get_by_id(vendor_id)
        if vendor is None or not vendor.is_active:
            return None
        vendor.name = data.name.strip()
        vendor.contact_person = data.contact_person.strip() or None
        vendor.phone = data.phone.strip() or None
        vendor.email = data.email.strip() or None
        vendor.address = data.address.strip() or None
        vendor.gst_number = data.gst_number.strip() or None
        vendor.remarks = data.remarks.strip() or None
        self.session.flush()
        return self.get_dto(vendor_id)

    def soft_delete(self, vendor_id: int) -> bool:
        """Mark vendor and its products inactive (preserves rows for future audit)."""
        vendor = self.get_by_id(vendor_id)
        if vendor is None or not vendor.is_active:
            return False
        vendor.is_active = False
        products = self.session.scalars(
            select(Product).where(Product.vendor_id == vendor_id, Product.is_active.is_(True))
        ).all()
        for product in products:
            product.is_active = False
        self.session.flush()
        return True
