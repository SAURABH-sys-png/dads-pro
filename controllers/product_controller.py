"""
Product management controller — CRUD inside Vendor Details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from PySide2.QtWidgets import QDialog

from services.product_service import ProductService
from utils.dialogs import ask_yes_no, show_error, show_info, show_warning
from utils.exceptions import AppError, NotFoundError, ValidationError
from utils.logger import get_logger, log_exception
from views.product_form_dialog import ProductFormDialog

if TYPE_CHECKING:
    from views.main_window import MainWindow

logger = get_logger("product_controller")


class ProductController:
    """Connects VendorDetailsView product grid to ProductService."""

    def __init__(self, window: "MainWindow") -> None:
        self.window = window
        self.service = ProductService()
        self._current_vendor_id: int | None = None
        self._connect()

    def _connect(self) -> None:
        details = self.window.vendor_details_view
        details.add_product_requested.connect(self.add_product)
        details.edit_product_requested.connect(self.edit_product)
        details.delete_products_requested.connect(self.delete_products)
        details.search_changed.connect(self.refresh_products)
        details.refresh_requested.connect(lambda: self.refresh_products())

    def load_products_for_vendor(self, vendor_id: int) -> None:
        self._current_vendor_id = vendor_id
        self.window.vendor_details_view.search_edit.clear()
        self.refresh_products()

    def refresh_products(self, search: str = "") -> None:
        if self._current_vendor_id is None:
            return
        try:
            term = search if search else self.window.vendor_details_view.search_edit.text()
            products = self.service.list_for_vendor(self._current_vendor_id, search=term)
            self.window.vendor_details_view.set_products(products)
            self.window.set_status(f"{len(products)} product(s) for vendor #{self._current_vendor_id}")
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to load products", exc)
            show_error(self.window, "Error", "Could not load products. See logs/.")

    def add_product(self) -> None:
        if self._current_vendor_id is None:
            return
        dialog = ProductFormDialog(
            vendor_id=self._current_vendor_id,
            categories=self.service.list_categories(),
            units=self.service.list_units(),
            parent=self.window,
        )
        if dialog.exec_() != QDialog.Accepted:
            return
        try:
            created = self.service.create_product(dialog.get_data())
            show_info(self.window, "Product Added", f"“{created.name}” was created.")
            self.refresh_products()
        except ValidationError as exc:
            show_warning(self.window, "Validation", exc.message)
        except AppError as exc:
            show_error(self.window, "Error", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to create product", exc)
            show_error(self.window, "Error", "Could not create product. See logs/.")

    def edit_product(self, product_id: int) -> None:
        try:
            product = self.service.get_product(product_id)
        except NotFoundError as exc:
            show_warning(self.window, "Not Found", exc.message)
            return
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to load product", exc)
            show_error(self.window, "Error", "Could not load product. See logs/.")
            return

        dialog = ProductFormDialog(
            vendor_id=product.vendor_id,
            categories=self.service.list_categories(),
            units=self.service.list_units(),
            parent=self.window,
            product=product,
        )
        if dialog.exec_() != QDialog.Accepted:
            return
        try:
            updated = self.service.update_product(product_id, dialog.get_data())
            show_info(self.window, "Product Updated", f"“{updated.name}” was saved.")
            self.refresh_products()
        except ValidationError as exc:
            show_warning(self.window, "Validation", exc.message)
        except AppError as exc:
            show_error(self.window, "Error", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to update product", exc)
            show_error(self.window, "Error", "Could not update product. See logs/.")

    def delete_products(self, product_ids: List[int]) -> None:
        if not product_ids:
            show_warning(self.window, "Delete", "Select one or more products to delete.")
            return
        if not ask_yes_no(
            self.window,
            "Confirm Delete",
            f"Delete {len(product_ids)} product(s)?",
        ):
            return
        try:
            count = self.service.delete_products(product_ids)
            show_info(self.window, "Deleted", f"Removed {count} product(s).")
            self.refresh_products()
        except AppError as exc:
            show_error(self.window, "Error", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to delete products", exc)
            show_error(self.window, "Error", "Could not delete products. See logs/.")
