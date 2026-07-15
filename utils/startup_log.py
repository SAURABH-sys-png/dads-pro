"""
Very early startup logging written before Qt / SQLAlchemy load.

If the frozen exe fails on Windows 8 before the normal logger starts,
``logs/startup.log`` still captures the reason for USB field diagnosis.
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def startup_log_path() -> Path:
    log_dir = _app_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "startup.log"


def write_startup(message: str) -> None:
    """Append a timestamped line to logs/startup.log (best-effort)."""
    try:
        path = startup_log_path()
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{stamp} | {message}\n")
    except Exception:  # noqa: BLE001
        # Last resort: never crash because logging failed
        pass


def write_startup_exception(context: str, exc: BaseException) -> None:
    write_startup(f"ERROR [{context}]: {exc}")
    write_startup(traceback.format_exc())
