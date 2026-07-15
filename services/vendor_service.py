"""
Vendor service — validation and orchestration for vendor use-cases.
"""

from __future__ import annotations

import re
from typing import List, Optional

from database.connection import session_scope
from models.dto import VendorDTO
from repositories.vendor_repository import VendorRepository
from utils.exceptions import NotFoundError, ValidationError
from utils.logger import get_logger

logger = get_logger("vendor_service")

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class VendorService:
    """Business logic for Vendor Management."""

    def list_vendors(self, search: str = "") -> List[VendorDTO]:
        with session_scope() as session:
            return VendorRepository(session).list_all(search=search)

    def get_vendor(self, vendor_id: int) -> VendorDTO:
        with session_scope() as session:
            dto = VendorRepository(session).get_dto(vendor_id)
            if dto is None:
                raise NotFoundError(f"Vendor #{vendor_id} was not found.")
            return dto

    def create_vendor(self, data: VendorDTO) -> VendorDTO:
        self._validate(data)
        with session_scope() as session:
            created = VendorRepository(session).create(data)
            logger.info("Created vendor id=%s name=%r", created.id, created.name)
            return created

    def update_vendor(self, vendor_id: int, data: VendorDTO) -> VendorDTO:
        self._validate(data)
        with session_scope() as session:
            updated = VendorRepository(session).update(vendor_id, data)
            if updated is None:
                raise NotFoundError(f"Vendor #{vendor_id} was not found.")
            logger.info("Updated vendor id=%s", vendor_id)
            return updated

    def delete_vendor(self, vendor_id: int) -> None:
        with session_scope() as session:
            ok = VendorRepository(session).soft_delete(vendor_id)
            if not ok:
                raise NotFoundError(f"Vendor #{vendor_id} was not found.")
            logger.info("Soft-deleted vendor id=%s", vendor_id)

    @staticmethod
    def _validate(data: VendorDTO) -> None:
        name = (data.name or "").strip()
        if not name:
            raise ValidationError("Vendor name is required.")
        if len(name) > 200:
            raise ValidationError("Vendor name must be 200 characters or fewer.")

        email = (data.email or "").strip()
        if email and not _EMAIL_RE.match(email):
            raise ValidationError("Email address is not valid.")

        phone = (data.phone or "").strip()
        if phone and len(phone) > 30:
            raise ValidationError("Phone number is too long.")
