"""
Application-wide configuration constants.

All settings live here so the rest of the codebase has a single source of truth.
Paths are resolved via ``utils.paths`` to keep the app USB-portable.
"""

from __future__ import annotations

# Application identity
APP_NAME: str = "Inventory Manager"
APP_VERSION: str = "1.0.0"
ORGANIZATION_NAME: str = "Army Non-CSD Canteen"

# Local SQLite database file (stored next to the application)
DATABASE_FILENAME: str = "inventory.db"

# Folder names (relative to application root)
BACKUP_DIR_NAME: str = "backups"
LOG_DIR_NAME: str = "logs"
ASSETS_DIR_NAME: str = "assets"
ICONS_DIR_NAME: str = "icons"

# Logging
LOG_FILENAME: str = "app.log"
LOG_MAX_BYTES: int = 2 * 1024 * 1024  # 2 MB
LOG_BACKUP_COUNT: int = 5

# UI defaults
MAIN_WINDOW_MIN_WIDTH: int = 1024
MAIN_WINDOW_MIN_HEIGHT: int = 700
DEFAULT_WINDOW_TITLE: str = f"{APP_NAME} v{APP_VERSION}"

# Seed reference data inserted on first run
DEFAULT_UNITS: tuple[str, ...] = (
    "Piece",
    "Box",
    "Packet",
    "Kg",
    "Gram",
    "Litre",
    "Ml",
    "Dozen",
    "Carton",
    "Bag",
)

DEFAULT_CATEGORIES: tuple[str, ...] = (
    "General",
    "Grocery",
    "Beverages",
    "Snacks",
    "Personal Care",
    "Household",
    "Stationery",
    "Electronics",
    "Clothing",
    "Other",
)
