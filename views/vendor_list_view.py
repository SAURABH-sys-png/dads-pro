"""
Vendor list screen with search and CRUD toolbar.
"""

from __future__ import annotations

from typing import List

from utils.qt import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, Signal

from models.dto import VendorDTO
from views.widgets.excel_table import ExcelTableWidget


class VendorListView(QWidget):
    """Table of vendors with Add / Edit / Delete / Search."""

    back_requested = Signal()
    add_requested = Signal()
    edit_requested = Signal(int)
    delete_requested = Signal(list)
    view_requested = Signal(int)
    search_changed = Signal(str)

    COLUMNS = ["Vendor Name", "Phone", "GST", "Products Count", "Last Updated"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Vendor Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch(1)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name, phone, GST, contact…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setMinimumWidth(280)
        self.search_edit.textChanged.connect(self.search_changed.emit)
        header.addWidget(self.search_edit)
        layout.addLayout(header)

        toolbar = QHBoxLayout()
        self.btn_back = QPushButton("← Home")
        self.btn_add = QPushButton("Add Vendor")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        self.btn_view = QPushButton("View Details")
        self.btn_refresh = QPushButton("Refresh")

        self.btn_back.clicked.connect(self.back_requested.emit)
        self.btn_add.clicked.connect(self.add_requested.emit)
        self.btn_edit.clicked.connect(self._emit_edit)
        self.btn_delete.clicked.connect(self._emit_delete)
        self.btn_view.clicked.connect(self._emit_view)

        for btn in (
            self.btn_back,
            self.btn_add,
            self.btn_edit,
            self.btn_delete,
            self.btn_view,
            self.btn_refresh,
        ):
            toolbar.addWidget(btn)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.table = ExcelTableWidget()
        self.table.configure_columns(self.COLUMNS)
        self.table.edit_requested.connect(self.view_requested.emit)
        self.table.delete_requested.connect(self.delete_requested.emit)
        layout.addWidget(self.table)

        self.status_label = QLabel("0 vendors")
        layout.addWidget(self.status_label)

    def set_vendors(self, vendors: List[VendorDTO]) -> None:
        self.table.clear_rows()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(vendors))
        for row, vendor in enumerate(vendors):
            updated = (
                vendor.updated_at.strftime("%d-%m-%Y %H:%M")
                if vendor.updated_at
                else ""
            )
            self.table.set_row_values(
                row,
                int(vendor.id or 0),
                [
                    vendor.name,
                    vendor.phone,
                    vendor.gst_number,
                    str(vendor.products_count),
                    updated,
                ],
                sort_keys=[
                    vendor.name.lower(),
                    vendor.phone,
                    vendor.gst_number,
                    vendor.products_count,
                    vendor.updated_at or "",
                ],
            )
        self.table.setSortingEnabled(True)
        self.status_label.setText(f"{len(vendors)} vendor(s)")

    def selected_ids(self) -> List[int]:
        return self.table.selected_ids()

    def _emit_edit(self) -> None:
        ids = self.selected_ids()
        if ids:
            self.edit_requested.emit(ids[0])

    def _emit_delete(self) -> None:
        ids = self.selected_ids()
        if ids:
            self.delete_requested.emit(ids)

    def _emit_view(self) -> None:
        ids = self.selected_ids()
        if ids:
            self.view_requested.emit(ids[0])
