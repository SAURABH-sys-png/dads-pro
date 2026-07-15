"""
Vendor create / edit dialog.
"""

from __future__ import annotations

from typing import Optional

from PySide2.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from models.dto import VendorDTO


class VendorFormDialog(QDialog):
    """Modal form for adding or editing a vendor."""

    def __init__(self, parent=None, vendor: Optional[VendorDTO] = None) -> None:
        super().__init__(parent)
        self._vendor = vendor
        self.setWindowTitle("Edit Vendor" if vendor and vendor.id else "Add Vendor")
        self.setMinimumWidth(480)
        self._build_ui()
        if vendor:
            self._load(vendor)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.contact_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.gst_edit = QLineEdit()
        self.address_edit = QTextEdit()
        self.address_edit.setFixedHeight(70)
        self.remarks_edit = QTextEdit()
        self.remarks_edit.setFixedHeight(70)

        form.addRow("Vendor Name *", self.name_edit)
        form.addRow("Contact Person", self.contact_edit)
        form.addRow("Phone Number", self.phone_edit)
        form.addRow("Email", self.email_edit)
        form.addRow("GST Number", self.gst_edit)
        form.addRow("Address", self.address_edit)
        form.addRow("Remarks", self.remarks_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load(self, vendor: VendorDTO) -> None:
        self.name_edit.setText(vendor.name)
        self.contact_edit.setText(vendor.contact_person)
        self.phone_edit.setText(vendor.phone)
        self.email_edit.setText(vendor.email)
        self.gst_edit.setText(vendor.gst_number)
        self.address_edit.setPlainText(vendor.address)
        self.remarks_edit.setPlainText(vendor.remarks)

    def _on_accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Vendor name is required.")
            self.name_edit.setFocus()
            return
        self.accept()

    def get_data(self) -> VendorDTO:
        base = self._vendor or VendorDTO()
        return VendorDTO(
            id=base.id,
            name=self.name_edit.text().strip(),
            contact_person=self.contact_edit.text().strip(),
            phone=self.phone_edit.text().strip(),
            email=self.email_edit.text().strip(),
            address=self.address_edit.toPlainText().strip(),
            gst_number=self.gst_edit.text().strip(),
            remarks=self.remarks_edit.toPlainText().strip(),
            is_active=True,
            created_at=base.created_at,
            updated_at=base.updated_at,
            products_count=base.products_count,
        )
