@echo off
REM ============================================================
REM  Build portable Inventory Manager for Windows 8 (offline)
REM  Prefer: BUILD_WINDOWS8.bat from the project root (one-click).
REM  Requires: active venv with requirements-win8.txt installed.
REM ============================================================

setlocal
cd /d "%~dp0.."

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Create a venv first, or run BUILD_WINDOWS8.bat from the project root.
    exit /b 1
)

call venv\Scripts\activate.bat

python -c "import sys; raise SystemExit(0 if sys.version_info < (3,11) else 1)"
if errorlevel 1 (
    echo [ERROR] This venv is Python 3.11+. Rebuild with Python 3.10.11.
    exit /b 1
)

python -c "import PySide2" 2>nul
if errorlevel 1 (
    echo [ERROR] PySide2 missing. Run: pip install -r requirements-win8.txt
    exit /b 1
)

echo.
echo === Building InventoryManager (one-folder, no console) ===
pyinstaller --noconfirm --clean packaging\InventoryManager.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller failed.
    exit /b 1
)

echo.
echo === Flattening Qt plugins to platforms\ and styles\ ===
python packaging\post_build_flatten.py
if errorlevel 1 (
    echo [ERROR] Post-build flatten failed.
    exit /b 1
)

echo.
echo === Bundling Visual C++ runtime DLLs + START_HERE.bat ===
python packaging\copy_vcruntime.py

echo.
echo === Ensuring runtime folders ===
if not exist "dist\InventoryManager\backups" mkdir "dist\InventoryManager\backups"
if not exist "dist\InventoryManager\logs" mkdir "dist\InventoryManager\logs"
if not exist "dist\InventoryManager\assets" mkdir "dist\InventoryManager\assets"
if not exist "dist\InventoryManager\icons" mkdir "dist\InventoryManager\icons"

echo.
echo Build complete.
echo Copy the ENTIRE folder to USB:
echo   dist\InventoryManager\
echo.
echo On the target Windows 8 PC, double-click InventoryManager.exe
echo No Python install and no internet required.
endlocal
