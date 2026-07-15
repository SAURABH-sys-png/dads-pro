"""
Vendor management controller — list, CRUD, and navigation to details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from utils.qt import QDialog, qt_exec

from services.vendor_service import VendorService
from utils.dialogs import ask_yes_no, show_error, show_info, show_warning
from utils.exceptions import AppError, NotFoundError, ValidationError
from utils.logger import get_logger, log_exception
from views.vendor_form_dialog import VendorFormDialog

if TYPE_CHECKING:
    from controllers.product_controller import ProductController
    from views.main_window import MainWindow

logger = get_logger("vendor_controller")


class VendorController:
    """Connects VendorListView / VendorDetailsView to VendorService."""

    def __init__(self, window: "MainWindow", product_controller: "ProductController") -> None:
        self.window = window
        self.product_controller = product_controller
        self.service = VendorService()
        self._connect()

    def _connect(self) -> None:
        home = self.window.home_view
        home.open_vendors.connect(self.open_vendor_list)

        view = self.window.vendor_list_view
        view.back_requested.connect(self.window.show_home)
        view.add_requested.connect(self.add_vendor)
        view.edit_requested.connect(self.edit_vendor)
        view.delete_requested.connect(self.delete_vendors)
        view.view_requested.connect(self.open_vendor_details)
        view.search_changed.connect(self.refresh_list)
        view.btn_refresh.clicked.connect(lambda: self.refresh_list())

        details = self.window.vendor_details_view
        details.back_requested.connect(self.open_vendor_list)
        details.edit_vendor_requested.connect(self.edit_vendor)

    def open_vendor_list(self) -> None:
        self.refresh_list()
        self.window.show_vendors()

    def refresh_list(self, search: str = "") -> None:
        try:
            term = search if search else self.window.vendor_list_view.search_edit.text()
            vendors = self.service.list_vendors(search=term)
            self.window.vendor_list_view.set_vendors(vendors)
            self.window.set_status(f"{len(vendors)} vendor(s) loaded")
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to load vendors", exc)
            show_error(self.window, "Error", "Could not load vendors. See logs/.")

    def add_vendor(self) -> None:
        dialog = VendorFormDialog(self.window)
        if qt_exec(dialog) != QDialog.Accepted:
            return
        try:
            created = self.service.create_vendor(dialog.get_data())
            show_info(self.window, "Vendor Added", f"“{created.name}” was created.")
            self.refresh_list()
        except ValidationError as exc:
            show_warning(self.window, "Validation", exc.message)
        except AppError as exc:
            show_error(self.window, "Error", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to create vendor", exc)
            show_error(self.window, "Error", "Could not create vendor. See logs/.")

    def edit_vendor(self, vendor_id: int) -> None:
        try:
            vendor = self.service.get_vendor(vendor_id)
        except NotFoundError as exc:
            show_warning(self.window, "Not Found", exc.message)
            return
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to load vendor", exc)
            show_error(self.window, "Error", "Could not load vendor. See logs/.")
            return

        dialog = VendorFormDialog(self.window, vendor=vendor)
        if qt_exec(dialog) != QDialog.Accepted:
            return
        try:
            updated = self.service.update_vendor(vendor_id, dialog.get_data())
            show_info(self.window, "Vendor Updated", f"“{updated.name}” was saved.")
            self.refresh_list()
            # Refresh details header if currently viewing this vendor
            details = self.window.vendor_details_view
            if details.vendor_id == vendor_id:
                details.set_vendor(updated)
        except ValidationError as exc:
            show_warning(self.window, "Validation", exc.message)
        except AppError as exc:
            show_error(self.window, "Error", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to update vendor", exc)
            show_error(self.window, "Error", "Could not update vendor. See logs/.")

    def delete_vendors(self, vendor_ids: List[int]) -> None:
        if not vendor_ids:
            show_warning(self.window, "Delete", "Select one or more vendors to delete.")
            return
        if not ask_yes_no(
            self.window,
            "Confirm Delete",
            f"Delete {len(vendor_ids)} vendor(s)?\n"
            "Products under these vendors will no longer appear in active lists.",
        ):
            return
        try:
            for vid in vendor_ids:
                self.service.delete_vendor(vid)
            show_info(self.window, "Deleted", f"Removed {len(vendor_ids)} vendor(s).")
            self.refresh_list()
        except AppError as exc:
            show_error(self.window, "Error", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to delete vendors", exc)
            show_error(self.window, "Error", "Could not delete vendors. See logs/.")

    def open_vendor_details(self, vendor_id: int) -> None:
        try:
            vendor = self.service.get_vendor(vendor_id)
            self.window.vendor_details_view.set_vendor(vendor)
            self.product_controller.load_products_for_vendor(vendor_id)
            self.window.show_vendor_details()
        except NotFoundError as exc:
            show_warning(self.window, "Not Found", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Failed to open vendor details", exc)
            show_error(self.window, "Error", "Could not open vendor details. See logs/.")
