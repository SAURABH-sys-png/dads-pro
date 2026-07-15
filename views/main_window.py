"""
Main application window — hosts a QStackedWidget of screens.
"""

from __future__ import annotations

from PySide2.QtWidgets import QMainWindow, QStackedWidget, QStatusBar

from config.settings import DEFAULT_WINDOW_TITLE, MAIN_WINDOW_MIN_HEIGHT, MAIN_WINDOW_MIN_WIDTH
from views.home_view import HomeView
from views.settings_view import SettingsView
from views.vendor_details_view import VendorDetailsView
from views.vendor_list_view import VendorListView


class MainWindow(QMainWindow):
    """
    Shell window. Controllers navigate by calling ``show_*`` helpers.

    Page indices are stable so future modules (Sales, Reports, …) can be
    inserted into the stack without rewriting existing screens.
    """

    PAGE_HOME = 0
    PAGE_VENDORS = 1
    PAGE_VENDOR_DETAILS = 2
    PAGE_SETTINGS = 3

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(DEFAULT_WINDOW_TITLE)
        self.setMinimumSize(MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT)

        self.stack = QStackedWidget()
        self.home_view = HomeView()
        self.vendor_list_view = VendorListView()
        self.vendor_details_view = VendorDetailsView()
        self.settings_view = SettingsView()

        self.stack.addWidget(self.home_view)              # 0
        self.stack.addWidget(self.vendor_list_view)       # 1
        self.stack.addWidget(self.vendor_details_view)    # 2
        self.stack.addWidget(self.settings_view)          # 3

        self.setCentralWidget(self.stack)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready — offline mode")

        self.show_home()

    def show_home(self) -> None:
        self.stack.setCurrentIndex(self.PAGE_HOME)

    def show_vendors(self) -> None:
        self.stack.setCurrentIndex(self.PAGE_VENDORS)

    def show_vendor_details(self) -> None:
        self.stack.setCurrentIndex(self.PAGE_VENDOR_DETAILS)

    def show_settings(self) -> None:
        self.stack.setCurrentIndex(self.PAGE_SETTINGS)

    def set_status(self, message: str) -> None:
        self.statusBar().showMessage(message)
