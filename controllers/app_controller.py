"""
Main application controller — wires home screen and global actions.
"""

from __future__ import annotations

from pathlib import Path

from utils.qt import QFileDialog

from services.backup_service import BackupService
from utils.dialogs import ask_yes_no, show_error, show_info
from utils.exceptions import AppError
from utils.logger import get_logger, log_exception
from views.main_window import MainWindow

logger = get_logger("app_controller")


class AppController:
    """
    Top-level controller.

    Owns the main window and delegates vendor/product flows to specialized
    controllers while handling Backup / Restore / Exit / Settings.
    """

    def __init__(self, window: MainWindow) -> None:
        self.window = window
        self.backup_service = BackupService()
        self._connect_home()
        self._connect_settings()

    def _connect_home(self) -> None:
        home = self.window.home_view
        home.open_settings.connect(self.window.show_settings)
        home.backup_database.connect(self.on_backup)
        home.restore_database.connect(self.on_restore)
        home.exit_app.connect(self.on_exit)

    def _connect_settings(self) -> None:
        self.window.settings_view.back_requested.connect(self.window.show_home)

    def on_backup(self) -> None:
        try:
            path = self.backup_service.create_backup()
            show_info(
                self.window,
                "Backup Complete",
                f"Database backup saved to:\n{path}",
            )
            self.window.set_status(f"Backup created: {path.name}")
        except AppError as exc:
            show_error(self.window, "Backup Failed", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Unexpected backup failure", exc)
            show_error(self.window, "Backup Failed", "An unexpected error occurred. See logs/.")

    def on_restore(self) -> None:
        backups = self.backup_service.list_backups()
        start_dir = str(backups[0].parent) if backups else str(Path.cwd())
        path_str, _ = QFileDialog.getOpenFileName(
            self.window,
            "Select Backup to Restore",
            start_dir,
            "SQLite Database (*.db);;All Files (*)",
        )
        if not path_str:
            return
        if not ask_yes_no(
            self.window,
            "Confirm Restore",
            "Restoring will replace the current database.\n"
            "A safety copy of the current database will be kept in backups/.\n\n"
            "Continue?",
        ):
            return
        try:
            self.backup_service.restore_backup(Path(path_str))
            show_info(
                self.window,
                "Restore Complete",
                "Database restored successfully.\nVendor list will refresh when you open it.",
            )
            self.window.set_status("Database restored")
            self.window.show_home()
        except AppError as exc:
            show_error(self.window, "Restore Failed", exc.message)
        except Exception as exc:  # noqa: BLE001
            log_exception(logger, "Unexpected restore failure", exc)
            show_error(self.window, "Restore Failed", "An unexpected error occurred. See logs/.")

    def on_exit(self) -> None:
        if ask_yes_no(self.window, "Exit", "Close Inventory Manager?"):
            self.window.close()
