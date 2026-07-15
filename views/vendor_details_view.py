"""
Vendor details page: vendor info header + Excel-like product grid.
"""

from __future__ import annotations

from typing import List, Optional

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.dto import ProductDTO, VendorDTO
from views.widgets.excel_table import ExcelTableWidget


class VendorDetailsView(QWidget):
    """Shows one vendor and all of its products."""

    back_requested = Signal()
    edit_vendor_requested = Signal(int)
    add_product_requested = Signal()
    edit_product_requested = Signal(int)
    delete_products_requested = Signal(list)
    search_changed = Signal(str)
    refresh_requested = Signal()

    PRODUCT_COLUMNS = [
        "Product Name",
        "Category",
        "Company",
        "SKU",
        "Batch Number",
        "Purchase Price",
        "Selling Price",
        "MRP",
        "GST %",
        "Stock Quantity",
        "Minimum Stock",
        "Unit",
        "Manufacturing Date",
        "Expiry Date",
        "Remarks",
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._vendor_id: Optional[int] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top = QHBoxLayout()
        self.btn_back = QPushButton("← Vendors")
        self.btn_back.clicked.connect(self.back_requested.emit)
        self.title_label = QLabel("Vendor Details")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.btn_edit_vendor = QPushButton("Edit Vendor")
        self.btn_edit_vendor.clicked.connect(self._emit_edit_vendor)
        top.addWidget(self.btn_back)
        top.addWidget(self.title_label)
        top.addStretch(1)
        top.addWidget(self.btn_edit_vendor)
        layout.addLayout(top)

        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QFormLayout(info_frame)
        self.lbl_name = QLabel("-")
        self.lbl_contact = QLabel("-")
        self.lbl_phone = QLabel("-")
        self.lbl_email = QLabel("-")
        self.lbl_gst = QLabel("-")
        self.lbl_address = QLabel("-")
        self.lbl_remarks = QLabel("-")
        self.lbl_dates = QLabel("-")
        for label in (
            self.lbl_name,
            self.lbl_contact,
            self.lbl_phone,
            self.lbl_email,
            self.lbl_gst,
            self.lbl_address,
            self.lbl_remarks,
            self.lbl_dates,
        ):
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        info_layout.addRow("Vendor Name:", self.lbl_name)
        info_layout.addRow("Contact Person:", self.lbl_contact)
        info_layout.addRow("Phone:", self.lbl_phone)
        info_layout.addRow("Email:", self.lbl_email)
        info_layout.addRow("GST Number:", self.lbl_gst)
        info_layout.addRow("Address:", self.lbl_address)
        info_layout.addRow("Remarks:", self.lbl_remarks)
        info_layout.addRow("Created / Updated:", self.lbl_dates)
        layout.addWidget(info_frame)

        prod_header = QHBoxLayout()
        prod_title = QLabel("Products")
        prod_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        prod_header.addWidget(prod_title)
        prod_header.addStretch(1)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search products by name, SKU, category…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setMinimumWidth(260)
        self.search_edit.textChanged.connect(self.search_changed.emit)
        prod_header.addWidget(self.search_edit)
        layout.addLayout(prod_header)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Add Product")
        self.btn_edit = QPushButton("Edit Product")
        self.btn_delete = QPushButton("Delete")
        self.btn_export = QPushButton("Export")
        self.btn_refresh = QPushButton("Refresh")

        self.btn_add.clicked.connect(self.add_product_requested.emit)
        self.btn_edit.clicked.connect(self._emit_edit_product)
        self.btn_delete.clicked.connect(self._emit_delete_products)
        self.btn_export.clicked.connect(self._export)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)

        for btn in (
            self.btn_add,
            self.btn_edit,
            self.btn_delete,
            self.btn_export,
            self.btn_refresh,
        ):
            toolbar.addWidget(btn)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.table = ExcelTableWidget()
        self.table.configure_columns(self.PRODUCT_COLUMNS)
        self.table.edit_requested.connect(self.edit_product_requested.emit)
        self.table.delete_requested.connect(self.delete_products_requested.emit)
        layout.addWidget(self.table)

        self.status_label = QLabel("0 products")
        layout.addWidget(self.status_label)

    @property
    def vendor_id(self) -> Optional[int]:
        return self._vendor_id

    def set_vendor(self, vendor: VendorDTO) -> None:
        self._vendor_id = vendor.id
        self.title_label.setText(f"Vendor Details — {vendor.name}")
        self.lbl_name.setText(vendor.name or "-")
        self.lbl_contact.setText(vendor.contact_person or "-")
        self.lbl_phone.setText(vendor.phone or "-")
        self.lbl_email.setText(vendor.email or "-")
        self.lbl_gst.setText(vendor.gst_number or "-")
        self.lbl_address.setText(vendor.address or "-")
        self.lbl_remarks.setText(vendor.remarks or "-")
        created = vendor.created_at.strftime("%d-%m-%Y %H:%M") if vendor.created_at else "-"
        updated = vendor.updated_at.strftime("%d-%m-%Y %H:%M") if vendor.updated_at else "-"
        self.lbl_dates.setText(f"{created}  /  {updated}")

    def set_products(self, products: List[ProductDTO]) -> None:
        self.table.clear_rows()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            mfg = p.manufacturing_date.strftime("%d-%m-%Y") if p.manufacturing_date else ""
            exp = p.expiry_date.strftime("%d-%m-%Y") if p.expiry_date else ""
            self.table.set_row_values(
                row,
                int(p.id or 0),
                [
                    p.name,
                    p.category_name,
                    p.company,
                    p.sku,
                    p.batch_number,
                    f"{p.purchase_price:.2f}",
                    f"{p.selling_price:.2f}",
                    f"{p.mrp:.2f}",
                    f"{p.gst_percent:.2f}",
                    f"{p.stock_quantity:.2f}",
                    f"{p.minimum_stock:.2f}",
                    p.unit_name,
                    mfg,
                    exp,
                    p.remarks,
                ],
                sort_keys=[
                    p.name.lower(),
                    p.category_name.lower(),
                    p.company.lower(),
                    p.sku.lower(),
                    p.batch_number.lower(),
                    p.purchase_price,
                    p.selling_price,
                    p.mrp,
                    p.gst_percent,
                    p.stock_quantity,
                    p.minimum_stock,
                    p.unit_name.lower(),
                    p.manufacturing_date or "",
                    p.expiry_date or "",
                    p.remarks.lower(),
                ],
            )
        self.table.setSortingEnabled(True)
        self.status_label.setText(f"{len(products)} product(s)")

    def _emit_edit_vendor(self) -> None:
        if self._vendor_id is not None:
            self.edit_vendor_requested.emit(self._vendor_id)

    def _emit_edit_product(self) -> None:
        ids = self.table.selected_ids()
        if ids:
            self.edit_product_requested.emit(ids[0])

    def _emit_delete_products(self) -> None:
        ids = self.table.selected_ids()
        if ids:
            self.delete_products_requested.emit(ids)

    def _export(self) -> None:
        self.table.export_to_csv("products.csv")
