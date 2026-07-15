@echo off
REM ============================================================
REM  ONE-CLICK BUILD — Inventory Manager for Windows 8 (offline)
REM
REM  Prerequisites (on a Windows PC WITH internet, once):
REM    - Python 3.10.11 64-bit  (latest that still works with PySide2)
REM      https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
REM      During install: check "Add python.exe to PATH"
REM    - For Windows 8.0 (not 8.1): use Python 3.8.10 instead
REM
REM  After build, copy onto USB:
REM      dist\InventoryManager\
REM  On Windows 8: double-click InventoryManager.exe
REM ============================================================

setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo === Locating Python 3.8 / 3.9 / 3.10 ===
set "PY="

where py >nul 2>&1
if not errorlevel 1 (
    py -3.10 -c "import sys" >nul 2>&1 && set "PY=py -3.10"
    if not defined PY py -3.9 -c "import sys" >nul 2>&1 && set "PY=py -3.9"
    if not defined PY py -3.8 -c "import sys" >nul 2>&1 && set "PY=py -3.8"
)

if not defined PY (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found.
        echo Install Python 3.10.11 64-bit and tick "Add to PATH":
        echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
        exit /b 1
    )
    set "PY=python"
)

echo Using: %PY%
%PY% -c "import sys; print(sys.version)"
%PY% -c "import sys; raise SystemExit(0 if (3,8) <= sys.version_info[:2] <= (3,10) else 1)"
if errorlevel 1 (
    echo [ERROR] Need Python 3.8, 3.9, or 3.10 for Windows 8 builds.
    echo Python 3.11+ cannot install PySide2. Prefer 3.10.11.
    exit /b 1
)

echo.
echo === Creating / updating venv ===
if not exist "venv\Scripts\activate.bat" (
    %PY% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Could not create venv.
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo.
echo === Installing Windows 8 dependencies ===
python -m pip install --upgrade "pip<25" "setuptools<70" wheel
if errorlevel 1 (
    echo [ERROR] pip upgrade failed.
    exit /b 1
)
python -m pip install -r requirements-win8.txt
if errorlevel 1 (
    echo [ERROR] pip install failed. Confirm Python is 3.8-3.10.
    exit /b 1
)

python -c "import PySide2; print('PySide2 OK', PySide2.__version__)"
if errorlevel 1 (
    echo [ERROR] PySide2 did not import. Aborting.
    exit /b 1
)

echo.
echo === Building portable executable folder ===
call packaging\build_windows.bat
if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo  BUILD OK
echo.
echo  Copy this ENTIRE folder to the USB stick:
echo      %CD%\dist\InventoryManager\
echo.
echo  On Windows 8: open InventoryManager.exe  ^(or START_HERE.bat^)
echo  Diagnostics: logs\startup.log next to the exe
echo ============================================================
endlocal
