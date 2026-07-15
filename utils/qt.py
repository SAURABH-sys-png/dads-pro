"""
Qt binding shim — PySide6 on Linux / modern Windows, PySide2 for Win8 builds.

All UI modules import from here so business/controllers stay unchanged.
Usage::

    from utils.qt import Qt, Signal, QWidget, QDialog, ...
"""

from __future__ import annotations

QT_API: str

try:
    from PySide6.QtCore import QDate, Qt, Signal
    from PySide6.QtGui import QAction, QFont, QKeySequence
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QCheckBox,
        QComboBox,
        QDateEdit,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QStackedWidget,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_API = "PySide6"
except ImportError:  # Windows 8 offline packaging target
    from PySide2.QtCore import QDate, Qt, Signal
    from PySide2.QtGui import QFont, QKeySequence
    from PySide2.QtWidgets import (
        QAbstractItemView,
        QAction,
        QApplication,
        QCheckBox,
        QComboBox,
        QDateEdit,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QStackedWidget,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_API = "PySide2"


def qt_exec(widget) -> int:
    """Run a modal dialog / app event loop on both Qt5 and Qt6."""
    if hasattr(widget, "exec_"):
        return int(widget.exec_())
    return int(widget.exec())


__all__ = [
    "QT_API",
    "QAbstractItemView",
    "QAction",
    "QApplication",
    "QCheckBox",
    "QComboBox",
    "QDate",
    "QDateEdit",
    "QDialog",
    "QDialogButtonBox",
    "QDoubleSpinBox",
    "QFileDialog",
    "QFont",
    "QFormLayout",
    "QFrame",
    "QHBoxLayout",
    "QHeaderView",
    "QKeySequence",
    "QLabel",
    "QLineEdit",
    "QMainWindow",
    "QMenu",
    "QMessageBox",
    "QPushButton",
    "QSizePolicy",
    "QStackedWidget",
    "QStatusBar",
    "QTableWidget",
    "QTableWidgetItem",
    "QTextEdit",
    "Qt",
    "QVBoxLayout",
    "QWidget",
    "Signal",
    "qt_exec",
]
