"""
Post-build helper: flatten Qt plugins next to the exe.

Produces:

    InventoryManager/
        InventoryManager.exe
        platforms/qwindows.dll
        styles/...
        backups/
        logs/
        assets/
        icons/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def _find_dist_root() -> Path:
    root = Path(__file__).resolve().parent.parent
    dist = root / "dist" / "InventoryManager"
    if not dist.exists():
        raise SystemExit(f"dist folder not found: {dist}")
    return dist


def _copy_tree_merge(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dest / item.name
        if item.is_dir():
            _copy_tree_merge(item, target)
        else:
            shutil.copy2(item, target)


def flatten_plugins(dist: Path) -> None:
    search = [
        dist / "PySide2" / "plugins",
        dist / "_internal" / "PySide2" / "plugins",
        dist / "PySide2" / "Qt" / "plugins",
        dist / "_internal" / "PySide2" / "Qt" / "plugins",
    ]
    plugins_root = next((p for p in search if p.exists()), None)
    if plugins_root is None:
        print("WARNING: PySide2 plugins folder not found — check the build.")
        return

    for name in ("platforms", "styles", "imageformats", "iconengines"):
        src = plugins_root / name
        if src.exists():
            dest = dist / name
            print(f"  copying {src} -> {dest}")
            _copy_tree_merge(src, dest)

    # Verify the critical Windows platform plugin
    qwindows = dist / "platforms" / "qwindows.dll"
    if qwindows.exists():
        print(f"OK: {qwindows}")
    else:
        print(f"WARNING: missing {qwindows} — exe may fail on Windows 8")


def ensure_runtime_dirs(dist: Path) -> None:
    for name in ("backups", "logs", "assets", "icons"):
        (dist / name).mkdir(parents=True, exist_ok=True)
        keep = dist / name / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def main() -> int:
    dist = _find_dist_root()
    print(f"Flattening plugins in {dist}")
    flatten_plugins(dist)
    ensure_runtime_dirs(dist)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
