"""
Inventory Manager — offline desktop entry point.

Boot sequence:
1. Write early startup log (survives launch failures)
2. Ensure portable folders exist (backups/, logs/, …)
3. Initialize logging
4. Create / migrate SQLite schema and seed lookups
5. Build MainWindow + controllers
6. Start Qt event loop

GUI uses ``utils.qt`` shim:
- PySide6 on Linux / modern Windows (development)
- PySide2 on Windows 8 offline packaged builds
"""

from __future__ import annotations

import sys
import traceback


def main() -> int:
    # Startup log must work even if later imports fail.
    from utils.startup_log import write_startup, write_startup_exception

    write_startup("Process started")
    write_startup(f"Python {sys.version}")
    write_startup(f"Executable: {sys.executable}")
    write_startup(f"Frozen: {getattr(sys, 'frozen', False)}")
    write_startup(f"argv: {sys.argv!r}")

    try:
        from utils.paths import ensure_runtime_directories, get_app_root
        from utils.qt_plugins import configure_qt_plugin_path

        ensure_runtime_directories()
        write_startup(f"App root: {get_app_root()}")
        platforms = configure_qt_plugin_path()
        if platforms is not None:
            write_startup(f"Qt platforms path: {platforms}")
    except Exception as exc:  # noqa: BLE001
        write_startup_exception("ensure_runtime_directories", exc)
        return 1

    try:
        from utils.logger import get_logger, setup_logging

        setup_logging()
        logger = get_logger("main")
    except Exception as exc:  # noqa: BLE001
        write_startup_exception("setup_logging", exc)
        return 1

    try:
        from utils.qt import QT_API, QApplication, QMessageBox, qt_exec

        write_startup(f"Qt binding imported: {QT_API}")
    except Exception as exc:  # noqa: BLE001
        write_startup_exception("import_qt", exc)
        logger.error("Qt import failed: %s\n%s", exc, traceback.format_exc())
        return 1

    try:
        from config.settings import APP_NAME, ORGANIZATION_NAME
        from controllers.app_controller import AppController
        from controllers.product_controller import ProductController
        from controllers.vendor_controller import VendorController
        from database.schema import initialize_database
        from views.main_window import MainWindow
    except Exception as exc:  # noqa: BLE001
        write_startup_exception("import_application_modules", exc)
        logger.error("Module import failed: %s\n%s", exc, traceback.format_exc())
        return 1

    logger.info("Starting %s (%s)", APP_NAME, QT_API)
    write_startup(f"Starting {APP_NAME} with {QT_API}")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    write_startup("QApplication created")

    try:
        initialize_database()
        write_startup("Database initialized")
    except Exception as exc:  # noqa: BLE001
        write_startup_exception("initialize_database", exc)
        logger.error("Database init failed: %s\n%s", exc, traceback.format_exc())
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Could not initialize the local database.\n\n{exc}\n\n"
            "See logs/startup.log and logs/app.log for details.",
        )
        return 1

    try:
        window = MainWindow()
        product_controller = ProductController(window)
        vendor_controller = VendorController(window, product_controller)
        app_controller = AppController(window)
        # Keep controllers referenced for the application lifetime
        window._controllers = (  # noqa: SLF001
            app_controller,
            vendor_controller,
            product_controller,
        )
        window.show()
        write_startup("UI ready — entering event loop")
        logger.info("UI ready")
        return qt_exec(app)
    except Exception as exc:  # noqa: BLE001
        write_startup_exception("ui_startup", exc)
        logger.error("UI startup failed: %s\n%s", exc, traceback.format_exc())
        try:
            QMessageBox.critical(
                None,
                "Startup Error",
                f"The application failed to start.\n\n{exc}\n\n"
                "See logs/startup.log for details.",
            )
        except Exception:  # noqa: BLE001
            pass
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        try:
            from utils.startup_log import write_startup_exception

            write_startup_exception("fatal", exc)
        except Exception:  # noqa: BLE001
            pass
        raise
