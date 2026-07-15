"""
Product repository — all SQL for the products table lives here.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from models.dto import ProductDTO
from models.entities import Category, Product, Unit, Vendor
from repositories.base import BaseRepository


def _to_dto(product: Product) -> ProductDTO:
    return ProductDTO(
        id=product.id,
        vendor_id=product.vendor_id,
        category_id=product.category_id,
        unit_id=product.unit_id,
        name=product.name or "",
        company=product.company or "",
        sku=product.sku or "",
        batch_number=product.batch_number or "",
        purchase_price=float(product.purchase_price or 0),
        selling_price=float(product.selling_price or 0),
        mrp=float(product.mrp or 0),
        gst_percent=float(product.gst_percent or 0),
        stock_quantity=float(product.stock_quantity or 0),
        minimum_stock=float(product.minimum_stock or 0),
        manufacturing_date=product.manufacturing_date,
        expiry_date=product.expiry_date,
        remarks=product.remarks or "",
        is_active=bool(product.is_active),
        created_at=product.created_at,
        updated_at=product.updated_at,
        category_name=product.category.name if product.category else "",
        unit_name=product.unit.name if product.unit else "",
        vendor_name=product.vendor.name if product.vendor else "",
    )


class ProductRepository(BaseRepository[Product]):
    """Data-access API for products."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Product)

    def _base_query(self):
        return (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.unit),
                joinedload(Product.vendor),
            )
            .where(Product.is_active.is_(True))
        )

    def list_by_vendor(self, vendor_id: int, search: str = "") -> List[ProductDTO]:
        stmt = self._base_query().where(Product.vendor_id == vendor_id).order_by(Product.name.asc())
        term = search.strip()
        if term:
            like = f"%{term}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(like),
                    Product.sku.ilike(like),
                    Product.company.ilike(like),
                    Product.batch_number.ilike(like),
                    Category.name.ilike(like),
                )
            ).outerjoin(Category, Product.category_id == Category.id)
        products = self.session.scalars(stmt).unique().all()
        return [_to_dto(p) for p in products]

    def search_all(self, search: str) -> List[ProductDTO]:
        """Global product search (vendor name / product / sku / category)."""
        term = search.strip()
        stmt = self._base_query().order_by(Product.name.asc())
        if term:
            like = f"%{term}%"
            stmt = (
                stmt.outerjoin(Category, Product.category_id == Category.id)
                .outerjoin(Vendor, Product.vendor_id == Vendor.id)
                .where(
                    or_(
                        Product.name.ilike(like),
                        Product.sku.ilike(like),
                        Product.company.ilike(like),
                        Category.name.ilike(like),
                        Vendor.name.ilike(like),
                    )
                )
            )
        products = self.session.scalars(stmt).unique().all()
        return [_to_dto(p) for p in products]

    def get_dto(self, product_id: int) -> Optional[ProductDTO]:
        stmt = self._base_query().where(Product.id == product_id)
        product = self.session.scalars(stmt).unique().first()
        if product is None:
            return None
        return _to_dto(product)

    def create(self, data: ProductDTO) -> ProductDTO:
        product = Product(
            vendor_id=data.vendor_id,
            category_id=data.category_id,
            unit_id=data.unit_id,
            name=data.name.strip(),
            company=data.company.strip() or None,
            sku=data.sku.strip() or None,
            batch_number=data.batch_number.strip() or None,
            purchase_price=data.purchase_price,
            selling_price=data.selling_price,
            mrp=data.mrp,
            gst_percent=data.gst_percent,
            stock_quantity=data.stock_quantity,
            minimum_stock=data.minimum_stock,
            manufacturing_date=data.manufacturing_date,
            expiry_date=data.expiry_date,
            remarks=data.remarks.strip() or None,
            is_active=True,
        )
        self.add(product)
        self.session.refresh(product)
        return self.get_dto(product.id) or _to_dto(product)

    def update(self, product_id: int, data: ProductDTO) -> Optional[ProductDTO]:
        product = self.get_by_id(product_id)
        if product is None or not product.is_active:
            return None
        product.category_id = data.category_id
        product.unit_id = data.unit_id
        product.name = data.name.strip()
        product.company = data.company.strip() or None
        product.sku = data.sku.strip() or None
        product.batch_number = data.batch_number.strip() or None
        product.purchase_price = data.purchase_price
        product.selling_price = data.selling_price
        product.mrp = data.mrp
        product.gst_percent = data.gst_percent
        product.stock_quantity = data.stock_quantity
        product.minimum_stock = data.minimum_stock
        product.manufacturing_date = data.manufacturing_date
        product.expiry_date = data.expiry_date
        product.remarks = data.remarks.strip() or None
        self.session.flush()
        return self.get_dto(product_id)

    def soft_delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        if product is None or not product.is_active:
            return False
        product.is_active = False
        self.session.flush()
        return True

    def soft_delete_many(self, product_ids: List[int]) -> int:
        deleted = 0
        for pid in product_ids:
            if self.soft_delete(pid):
                deleted += 1
        return deleted
