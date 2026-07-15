"""
Friendly Qt dialog helpers used by controllers.
"""

from __future__ import annotations

from typing import Optional

from utils.qt import QMessageBox, QWidget


def show_info(parent: Optional[QWidget], title: str, message: str) -> None:
    QMessageBox.information(parent, title, message)


def show_warning(parent: Optional[QWidget], title: str, message: str) -> None:
    QMessageBox.warning(parent, title, message)


def show_error(parent: Optional[QWidget], title: str, message: str) -> None:
    QMessageBox.critical(parent, title, message)


def ask_yes_no(parent: Optional[QWidget], title: str, message: str) -> bool:
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    return reply == QMessageBox.Yes
