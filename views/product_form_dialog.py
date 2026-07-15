"""
Product create / edit dialog.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from PySide2.QtCore import QDate
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.dto import LookupDTO, ProductDTO


def _qdate(value: Optional[date]) -> QDate:
    if value is None:
        return QDate.currentDate()
    return QDate(value.year, value.month, value.day)


def _pydate(value: QDate) -> Optional[date]:
    if not value.isValid():
        return None
    return date(value.year(), value.month(), value.day())


class ProductFormDialog(QDialog):
    """Modal form for adding or editing a product under a vendor."""

    def __init__(
        self,
        vendor_id: int,
        categories: List[LookupDTO],
        units: List[LookupDTO],
        parent=None,
        product: Optional[ProductDTO] = None,
    ) -> None:
        super().__init__(parent)
        self._vendor_id = vendor_id
        self._product = product
        self._categories = categories
        self._units = units
        self.setWindowTitle("Edit Product" if product and product.id else "Add Product")
        self.setMinimumWidth(520)
        self._build_ui()
        if product:
            self._load(product)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.company_edit = QLineEdit()
        self.sku_edit = QLineEdit()
        self.batch_edit = QLineEdit()

        self.category_combo = QComboBox()
        self.category_combo.addItem("(None)", None)
        for cat in self._categories:
            self.category_combo.addItem(cat.name, cat.id)

        self.unit_combo = QComboBox()
        self.unit_combo.addItem("(None)", None)
        for unit in self._units:
            self.unit_combo.addItem(unit.name, unit.id)

        self.purchase_spin = self._money_spin()
        self.selling_spin = self._money_spin()
        self.mrp_spin = self._money_spin()
        self.gst_spin = QDoubleSpinBox()
        self.gst_spin.setRange(0, 100)
        self.gst_spin.setDecimals(2)
        self.gst_spin.setSuffix(" %")

        self.stock_spin = self._qty_spin()
        self.min_stock_spin = self._qty_spin()

        self.mfg_enabled = QCheckBox("Set")
        self.mfg_date = QDateEdit()
        self.mfg_date.setCalendarPopup(True)
        self.mfg_date.setDisplayFormat("dd-MM-yyyy")
        self.mfg_date.setDate(QDate.currentDate())
        self.mfg_date.setEnabled(False)
        self.mfg_enabled.toggled.connect(self.mfg_date.setEnabled)

        self.exp_enabled = QCheckBox("Set")
        self.exp_date = QDateEdit()
        self.exp_date.setCalendarPopup(True)
        self.exp_date.setDisplayFormat("dd-MM-yyyy")
        self.exp_date.setDate(QDate.currentDate())
        self.exp_date.setEnabled(False)
        self.exp_enabled.toggled.connect(self.exp_date.setEnabled)

        self.remarks_edit = QTextEdit()
        self.remarks_edit.setFixedHeight(60)

        form.addRow("Product Name *", self.name_edit)
        form.addRow("Category", self.category_combo)
        form.addRow("Company", self.company_edit)
        form.addRow("SKU", self.sku_edit)
        form.addRow("Batch Number", self.batch_edit)
        form.addRow("Purchase Price", self.purchase_spin)
        form.addRow("Selling Price", self.selling_spin)
        form.addRow("MRP", self.mrp_spin)
        form.addRow("GST %", self.gst_spin)
        form.addRow("Stock Quantity", self.stock_spin)
        form.addRow("Minimum Stock", self.min_stock_spin)
        form.addRow("Unit", self.unit_combo)

        mfg_row = QWidget()
        mfg_layout = QHBoxLayout(mfg_row)
        mfg_layout.setContentsMargins(0, 0, 0, 0)
        mfg_layout.addWidget(self.mfg_enabled)
        mfg_layout.addWidget(self.mfg_date)
        form.addRow("Manufacturing Date", mfg_row)

        exp_row = QWidget()
        exp_layout = QHBoxLayout(exp_row)
        exp_layout.setContentsMargins(0, 0, 0, 0)
        exp_layout.addWidget(self.exp_enabled)
        exp_layout.addWidget(self.exp_date)
        form.addRow("Expiry Date", exp_row)

        form.addRow("Remarks", self.remarks_edit)

        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _money_spin() -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, 1_000_000_000)
        spin.setDecimals(2)
        spin.setMaximumWidth(160)
        return spin

    @staticmethod
    def _qty_spin() -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, 1_000_000_000)
        spin.setDecimals(2)
        spin.setMaximumWidth(160)
        return spin

    def _load(self, product: ProductDTO) -> None:
        self.name_edit.setText(product.name)
        self.company_edit.setText(product.company)
        self.sku_edit.setText(product.sku)
        self.batch_edit.setText(product.batch_number)
        self.purchase_spin.setValue(product.purchase_price)
        self.selling_spin.setValue(product.selling_price)
        self.mrp_spin.setValue(product.mrp)
        self.gst_spin.setValue(product.gst_percent)
        self.stock_spin.setValue(product.stock_quantity)
        self.min_stock_spin.setValue(product.minimum_stock)
        self.remarks_edit.setPlainText(product.remarks)

        if product.manufacturing_date:
            self.mfg_enabled.setChecked(True)
            self.mfg_date.setDate(_qdate(product.manufacturing_date))
        if product.expiry_date:
            self.exp_enabled.setChecked(True)
            self.exp_date.setDate(_qdate(product.expiry_date))

        if product.category_id is not None:
            idx = self.category_combo.findData(product.category_id)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
        if product.unit_id is not None:
            idx = self.unit_combo.findData(product.unit_id)
            if idx >= 0:
                self.unit_combo.setCurrentIndex(idx)

    def _on_accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Product name is required.")
            self.name_edit.setFocus()
            return
        self.accept()

    def get_data(self) -> ProductDTO:
        base = self._product or ProductDTO()
        return ProductDTO(
            id=base.id,
            vendor_id=self._vendor_id,
            category_id=self.category_combo.currentData(),
            unit_id=self.unit_combo.currentData(),
            name=self.name_edit.text().strip(),
            company=self.company_edit.text().strip(),
            sku=self.sku_edit.text().strip(),
            batch_number=self.batch_edit.text().strip(),
            purchase_price=self.purchase_spin.value(),
            selling_price=self.selling_spin.value(),
            mrp=self.mrp_spin.value(),
            gst_percent=self.gst_spin.value(),
            stock_quantity=self.stock_spin.value(),
            minimum_stock=self.min_stock_spin.value(),
            manufacturing_date=_pydate(self.mfg_date.date()) if self.mfg_enabled.isChecked() else None,
            expiry_date=_pydate(self.exp_date.date()) if self.exp_enabled.isChecked() else None,
            remarks=self.remarks_edit.toPlainText().strip(),
            is_active=True,
        )
