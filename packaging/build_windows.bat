@echo off
REM ============================================================
REM  Build portable Inventory Manager for Windows 8 (offline)
REM  Run on a Windows PC with Python 3.8 / 3.9 / 3.10 installed.
REM ============================================================

setlocal
cd /d "%~dp0.."

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Create a venv first:
    echo   py -3.9 -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements-win8.txt
    exit /b 1
)

call venv\Scripts\activate.bat

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
