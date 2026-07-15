"""
Home / landing screen with primary module navigation.

Uses PySide2 / Qt 5.15 APIs for Windows 8 offline compatibility.
"""

from __future__ import annotations

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont
from PySide2.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config.settings import APP_NAME, APP_VERSION, ORGANIZATION_NAME


class HomeView(QWidget):
    """
    First screen: Vendor Management, Settings, Backup, Restore, Exit.
    """

    open_vendors = Signal()
    open_settings = Signal()
    backup_database = Signal()
    restore_database = Signal()
    exit_app = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(20)

        title = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            f"{ORGANIZATION_NAME}  ·  Phase 1 — Vendors & Products  ·  v{APP_VERSION}"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #555555;")

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(24)

        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(12)
        panel_layout.setContentsMargins(32, 28, 32, 28)

        buttons = [
            ("Vendor Management", self.open_vendors, True),
            ("Settings", self.open_settings, False),
            ("Backup Database", self.backup_database, False),
            ("Restore Database", self.restore_database, False),
            ("Exit", self.exit_app, False),
        ]

        for text, signal, primary in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(44)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            font = btn.font()
            font.setPointSize(11)
            btn.setFont(font)
            if primary:
                btn.setDefault(True)
                btn.setStyleSheet(
                    "QPushButton { background-color: #1f4e79; color: white; "
                    "border: none; padding: 8px 16px; }"
                    "QPushButton:hover { background-color: #2b6aa0; }"
                    "QPushButton:pressed { background-color: #183a5a; }"
                )
            else:
                btn.setStyleSheet("QPushButton { padding: 8px 16px; }")
            btn.clicked.connect(signal.emit)
            panel_layout.addWidget(btn)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(panel, stretch=0)
        row.addStretch(1)
        root.addLayout(row)
        root.addStretch(1)

        footer = QLabel("Offline · Local SQLite · USB portable — no internet required")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #777777; font-size: 11px;")
        root.addWidget(footer)
