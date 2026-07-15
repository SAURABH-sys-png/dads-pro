"""
Product service — validation and orchestration for product use-cases.
"""

from __future__ import annotations

from typing import List, Optional

from database.connection import session_scope
from models.dto import LookupDTO, ProductDTO
from repositories.lookup_repository import CategoryRepository, UnitRepository
from repositories.product_repository import ProductRepository
from repositories.vendor_repository import VendorRepository
from utils.exceptions import NotFoundError, ValidationError
from utils.logger import get_logger

logger = get_logger("product_service")


class ProductService:
    """Business logic for Product Management under a vendor."""

    def list_for_vendor(self, vendor_id: int, search: str = "") -> List[ProductDTO]:
        with session_scope() as session:
            return ProductRepository(session).list_by_vendor(vendor_id, search=search)

    def search_products(self, search: str) -> List[ProductDTO]:
        with session_scope() as session:
            return ProductRepository(session).search_all(search)

    def get_product(self, product_id: int) -> ProductDTO:
        with session_scope() as session:
            dto = ProductRepository(session).get_dto(product_id)
            if dto is None:
                raise NotFoundError(f"Product #{product_id} was not found.")
            return dto

    def create_product(self, data: ProductDTO) -> ProductDTO:
        self._validate(data)
        with session_scope() as session:
            if VendorRepository(session).get_dto(data.vendor_id) is None:
                raise NotFoundError(f"Vendor #{data.vendor_id} was not found.")
            created = ProductRepository(session).create(data)
            logger.info(
                "Created product id=%s name=%r vendor=%s",
                created.id,
                created.name,
                data.vendor_id,
            )
            return created

    def update_product(self, product_id: int, data: ProductDTO) -> ProductDTO:
        self._validate(data)
        with session_scope() as session:
            updated = ProductRepository(session).update(product_id, data)
            if updated is None:
                raise NotFoundError(f"Product #{product_id} was not found.")
            logger.info("Updated product id=%s", product_id)
            return updated

    def delete_product(self, product_id: int) -> None:
        with session_scope() as session:
            ok = ProductRepository(session).soft_delete(product_id)
            if not ok:
                raise NotFoundError(f"Product #{product_id} was not found.")
            logger.info("Soft-deleted product id=%s", product_id)

    def delete_products(self, product_ids: List[int]) -> int:
        with session_scope() as session:
            return ProductRepository(session).soft_delete_many(product_ids)

    def list_categories(self) -> List[LookupDTO]:
        with session_scope() as session:
            return CategoryRepository(session).list_active()

    def list_units(self) -> List[LookupDTO]:
        with session_scope() as session:
            return UnitRepository(session).list_active()

    @staticmethod
    def _validate(data: ProductDTO) -> None:
        name = (data.name or "").strip()
        if not name:
            raise ValidationError("Product name is required.")
        if data.vendor_id <= 0:
            raise ValidationError("A vendor must be selected for the product.")
        for label, value in (
            ("Purchase price", data.purchase_price),
            ("Selling price", data.selling_price),
            ("MRP", data.mrp),
            ("GST %", data.gst_percent),
            ("Stock quantity", data.stock_quantity),
            ("Minimum stock", data.minimum_stock),
        ):
            if value is None or value < 0:
                raise ValidationError(f"{label} cannot be negative.")
        if data.gst_percent > 100:
            raise ValidationError("GST % cannot exceed 100.")
        if (
            data.manufacturing_date
            and data.expiry_date
            and data.expiry_date < data.manufacturing_date
        ):
            raise ValidationError("Expiry date cannot be before manufacturing date.")
