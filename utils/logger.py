"""
Application logging setup.

Writes to ``logs/app.log`` with rotation and also mirrors to stderr
during development. Controllers should call ``log_exception`` on failures.
"""

from __future__ import annotations

import logging
import traceback
from logging.handlers import RotatingFileHandler
from typing import Optional

from config.settings import LOG_BACKUP_COUNT, LOG_FILENAME, LOG_MAX_BYTES
from utils.paths import get_log_dir


_LOGGER: Optional[logging.Logger] = None


def setup_logging() -> logging.Logger:
    """Configure and return the root application logger (idempotent)."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    log_dir = get_log_dir()
    log_file = log_dir / LOG_FILENAME

    logger = logging.getLogger("inventory_manager")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _LOGGER = logger
    logger.info("Logging initialized → %s", log_file)
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a child logger; ensures setup has been called."""
    base = setup_logging()
    if name:
        return base.getChild(name)
    return base


def log_exception(logger: logging.Logger, message: str, exc: BaseException) -> None:
    """Log an exception with full traceback for crash diagnosis."""
    logger.error("%s: %s\n%s", message, exc, traceback.format_exc())
