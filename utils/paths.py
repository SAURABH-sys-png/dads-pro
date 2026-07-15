"""
Portable path helpers for USB / offline deployment.

Resolves the application root whether running from source or from a
PyInstaller-frozen executable, then builds all data paths relative to it.
"""

from __future__ import annotations

import sys
from pathlib import Path

from config.settings import (
    ASSETS_DIR_NAME,
    BACKUP_DIR_NAME,
    DATABASE_FILENAME,
    ICONS_DIR_NAME,
    LOG_DIR_NAME,
)


def get_app_root() -> Path:
    """
    Return the directory that should hold inventory.db, backups/, and logs/.

    - Frozen (PyInstaller): folder containing the .exe
    - Source: project root (parent of this package's usage via main.py)
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # main.py lives at project root
    return Path(__file__).resolve().parent.parent


def ensure_runtime_directories() -> None:
    """Create required folders if they are missing (first-run / USB copy)."""
    root = get_app_root()
    for name in (BACKUP_DIR_NAME, LOG_DIR_NAME, ASSETS_DIR_NAME, ICONS_DIR_NAME):
        (root / name).mkdir(parents=True, exist_ok=True)


def get_database_path() -> Path:
    """Absolute path to the local SQLite database file."""
    return get_app_root() / DATABASE_FILENAME


def get_backup_dir() -> Path:
    """Absolute path to the backups directory."""
    path = get_app_root() / BACKUP_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_log_dir() -> Path:
    """Absolute path to the logs directory."""
    path = get_app_root() / LOG_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_assets_dir() -> Path:
    """Absolute path to the assets directory."""
    return get_app_root() / ASSETS_DIR_NAME


def get_icons_dir() -> Path:
    """Absolute path to the icons directory."""
    return get_app_root() / ICONS_DIR_NAME
