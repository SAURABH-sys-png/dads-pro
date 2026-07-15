"""
PyInstaller runtime hook — runs before main.py inside the frozen exe.

Ensures Qt can locate platform plugins on Windows 8 USB deployments.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure() -> None:
    if not getattr(sys, "frozen", False):
        return

    root = Path(sys.executable).resolve().parent

    # Preferred layout after post-build flatten: <root>/platforms/qwindows.dll
    candidates = [
        root / "platforms",
        root / "PySide2" / "plugins" / "platforms",
        root / "_internal" / "PySide2" / "plugins" / "platforms",
        root / "_internal" / "platforms",
    ]
    for platforms in candidates:
        if (platforms / "qwindows.dll").exists():
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms)
            os.environ["QT_PLUGIN_PATH"] = str(platforms.parent)
            break


_configure()
