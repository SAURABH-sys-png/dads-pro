"""
Backup and restore service for the local SQLite database.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from database.connection import reset_engine
from utils.exceptions import BackupError
from utils.logger import get_logger
from utils.paths import get_backup_dir, get_database_path

logger = get_logger("backup_service")


class BackupService:
    """One-click backup / restore of inventory.db into /backups."""

    def create_backup(self) -> Path:
        """Copy the live database into a timestamped file under backups/."""
        db_path = get_database_path()
        if not db_path.exists():
            raise BackupError("Database file does not exist yet.")

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = get_backup_dir() / f"inventory_backup_{stamp}.db"
        try:
            # Also copy SQLite WAL companions if present
            shutil.copy2(db_path, dest)
            for suffix in ("-wal", "-shm"):
                side = Path(str(db_path) + suffix)
                if side.exists():
                    shutil.copy2(side, Path(str(dest) + suffix))
            logger.info("Backup created: %s", dest)
            return dest
        except OSError as exc:
            raise BackupError(f"Could not create backup: {exc}") from exc

    def list_backups(self) -> List[Path]:
        backup_dir = get_backup_dir()
        files = sorted(backup_dir.glob("inventory_backup_*.db"), reverse=True)
        return files

    def restore_backup(self, backup_path: Path) -> None:
        """
        Replace the live database with a chosen backup.

        Closes the SQLAlchemy engine afterward so the next query uses the
        restored file.
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise BackupError(f"Backup file not found: {backup_path}")

        db_path = get_database_path()
        try:
            reset_engine()
            # Safety copy of current DB before overwrite
            if db_path.exists():
                safety = get_backup_dir() / (
                    f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                )
                shutil.copy2(db_path, safety)
            shutil.copy2(backup_path, db_path)
            # Drop stale WAL so SQLite opens the restored main file cleanly
            for suffix in ("-wal", "-shm"):
                side = Path(str(db_path) + suffix)
                if side.exists():
                    side.unlink()
            reset_engine()
            logger.info("Restored database from %s", backup_path)
        except OSError as exc:
            raise BackupError(f"Could not restore backup: {exc}") from exc
