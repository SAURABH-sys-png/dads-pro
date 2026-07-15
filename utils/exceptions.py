"""
Domain-specific exceptions used across services and controllers.

Controllers catch these and show friendly Qt dialogs instead of crashing.
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for all application errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    """Raised when user input fails business validation rules."""


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""


class DatabaseError(AppError):
    """Raised when a database operation fails unexpectedly."""


class BackupError(AppError):
    """Raised when backup or restore operations fail."""
