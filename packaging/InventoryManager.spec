# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — portable one-folder build for Windows 8 offline deploy.

Build on a Windows PC (Python 3.8–3.10 + PySide2). Prefer:

    BUILD_WINDOWS8.bat

Or manually:

    packaging\\build_windows.bat
"""

import os

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_all

# SPECPATH is injected by PyInstaller (directory containing this .spec file)
ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))  # noqa: F821

block_cipher = None

pyside2_datas, pyside2_binaries, pyside2_hiddenimports = collect_all("PySide2")

datas = [
    (os.path.join(ROOT, "assets", ".gitkeep"), "assets"),
    (os.path.join(ROOT, "icons", ".gitkeep"), "icons"),
    (os.path.join(ROOT, "backups", ".gitkeep"), "backups"),
    (os.path.join(ROOT, "logs", ".gitkeep"), "logs"),
]
datas += pyside2_datas

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=pyside2_binaries,
    datas=datas,
    hiddenimports=pyside2_hiddenimports
    + [
        "sqlalchemy",
        "sqlalchemy.dialects.sqlite",
        "greenlet",
        "config.settings",
        "database.connection",
        "database.schema",
        "models.entities",
        "models.dto",
        "repositories.vendor_repository",
        "repositories.product_repository",
        "repositories.lookup_repository",
        "services.vendor_service",
        "services.product_service",
        "services.backup_service",
        "controllers.app_controller",
        "controllers.vendor_controller",
        "controllers.product_controller",
        "views.main_window",
        "views.home_view",
        "views.vendor_list_view",
        "views.vendor_details_view",
        "views.vendor_form_dialog",
        "views.product_form_dialog",
        "views.settings_view",
        "views.widgets.excel_table",
        "utils.paths",
        "utils.logger",
        "utils.startup_log",
        "utils.qt_plugins",
        "utils.dialogs",
        "utils.exceptions",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(ROOT, "packaging", "runtime_hook_qt.py")],
    excludes=[
        "matplotlib",
        "numpy",
        "PIL",
        "tkinter",
        "PySide6",
        "shiboken6",
        "PyQt5",
        "PyQt6",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="InventoryManager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="InventoryManager",
)
