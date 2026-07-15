"""
Copy Visual C++ 2015–2022 redistributable DLLs next to the frozen exe.

Windows 8 machines without the VC++ runtime installed fail immediately
with a missing-DLL dialog. Bundling these next to InventoryManager.exe
makes the USB copy self-contained for non-technical users.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


DLL_NAMES = (
    "VCRUNTIME140.dll",
    "VCRUNTIME140_1.dll",
    "MSVCP140.dll",
    "MSVCP140_1.dll",
    "MSVCP140_2.dll",
    "CONCRT140.dll",
)


def _candidate_dirs() -> list[Path]:
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    roots = [
        windir / "System32",
        windir / "SysWOW64",
    ]
    # Also probe common redist install locations
    program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    for base in (program_files, program_files_x86):
        roots.append(base / "Microsoft Visual Studio" / "2022" / "BuildTools" / "VC" / "Redist")
    return roots


def _find_dll(name: str) -> Path | None:
    for root in _candidate_dirs():
        if not root.exists():
            continue
        direct = root / name
        if direct.is_file():
            return direct
        # shallow walk for nested redist folders
        try:
            for path in root.rglob(name):
                if path.is_file():
                    return path
        except (OSError, PermissionError):
            continue
    return None


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    dist = root / "dist" / "InventoryManager"
    if not dist.is_dir():
        print(f"dist folder missing: {dist}")
        return 1

    copied = 0
    for name in DLL_NAMES:
        dest = dist / name
        if dest.exists():
            print(f"  already present: {name}")
            continue
        src = _find_dll(name)
        if src is None:
            print(f"  not found on build PC: {name}")
            continue
        shutil.copy2(src, dest)
        print(f"  copied {src} -> {dest}")
        copied += 1

    # Friendly double-click helper for end users
    launcher = dist / "START_HERE.bat"
    launcher.write_text(
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "start \"\" \"InventoryManager.exe\"\r\n",
        encoding="utf-8",
    )
    print(f"  wrote {launcher}")
    print(f"Done. Copied {copied} runtime DLL(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
