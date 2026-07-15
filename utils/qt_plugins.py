"""
Qt plugin path helpers for PyInstaller one-folder deployments.

On Windows 8 USB copies, the exe must find qwindows.dll under platforms/.
This module probes common layouts and sets the Qt environment variables
before QApplication is created.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional


def _candidates(root: Path) -> List[Path]:
    return [
        root / "platforms",
        root / "styles",
        root / "PySide2" / "plugins",
        root / "PySide2" / "plugins" / "platforms",
        root / "_internal" / "PySide2" / "plugins",
        root / "_internal" / "PySide2" / "plugins" / "platforms",
        root / "_internal" / "platforms",
    ]


def find_platforms_dir(root: Path) -> Optional[Path]:
    for path in _candidates(root):
        if path.name == "platforms" and (path / "qwindows.dll").exists():
            return path
        nested = path / "platforms" / "qwindows.dll"
        if nested.exists():
            return nested.parent
    return None


def configure_qt_plugin_path() -> Optional[Path]:
    """
    Set QT_PLUGIN_PATH / QT_QPA_PLATFORM_PLUGIN_PATH for frozen builds.

    Returns the platforms directory if found.
    """
    if not getattr(sys, "frozen", False):
        return None

    root = Path(sys.executable).resolve().parent
    platforms = find_platforms_dir(root)
    if platforms is None:
        return None

    plugins_root = platforms.parent
    os.environ.setdefault("QT_PLUGIN_PATH", str(plugins_root))
    os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(platforms))
    return platforms
