"""
Simple Settings screen (placeholder for Phase 1 — ready for future options).
"""

from __future__ import annotations

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QFormLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from config.settings import APP_NAME, APP_VERSION
from utils.paths import get_app_root, get_database_path


class SettingsView(QWidget):
    """Shows local paths and offline configuration summary."""

    back_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.addRow("Application:", QLabel(f"{APP_NAME} v{APP_VERSION}"))
        form.addRow("Mode:", QLabel("Fully offline (no internet required)"))
        form.addRow("App folder:", QLabel(str(get_app_root())))
        form.addRow("Database:", QLabel(str(get_database_path())))
        form.addRow("Login:", QLabel("Not required (Phase 1)"))
        layout.addLayout(form)

        note = QLabel(
            "Future settings (theme, GST defaults, barcode, users/permissions) "
            "will appear here without changing the core architecture."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #555555; margin-top: 12px;")
        layout.addWidget(note)
        layout.addStretch(1)

        btn = QPushButton("← Back to Home")
        btn.clicked.connect(self.back_requested.emit)
        layout.addWidget(btn)
