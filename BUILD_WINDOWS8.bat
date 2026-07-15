@echo off
REM ============================================================
REM  ONE-CLICK BUILD — Inventory Manager for Windows 8 (offline)
REM
REM  Install Python 3.10.11 FIRST (tick "Add to PATH"):
REM    https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
REM  Windows 8.0 (not 8.1): use Python 3.8.10 instead.
REM
REM  This window STAYS OPEN so you can read errors.
REM  A full log is also written to: build_log.txt
REM ============================================================

setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "LOG=%~dp0build_log.txt"
echo. > "%LOG%"
call :log ============================================================
call :log Inventory Manager — Windows 8 build
call :log Started: %DATE% %TIME%
call :log Folder: %CD%
call :log ============================================================

REM --- Find a usable Python 3.8 / 3.9 / 3.10 ---
set "PYTHON_EXE="

where py >nul 2>&1
if not errorlevel 1 (
  call :log py launcher found — probing 3.10 / 3.9 / 3.8
  for %%V in (3.10 3.9 3.8) do (
    if not defined PYTHON_EXE (
      py -%%V -c "import sys" >nul 2>&1
      if not errorlevel 1 (
        for /f "delims=" %%P in ('py -%%V -c "import sys; print(sys.executable)" 2^>nul') do (
          set "PYTHON_EXE=%%P"
          call :log Selected via py -%%V : %%P
        )
      )
    )
  )
)

if not defined PYTHON_EXE (
  where python >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
    call :log Selected via python : !PYTHON_EXE!
  )
)

if not defined PYTHON_EXE (
  call :log [ERROR] No Python found on PATH.
  echo.
  echo [ERROR] Python 3.8 / 3.9 / 3.10 is not installed ^(or not on PATH^).
  echo.
  echo Install Python 3.10.11 64-bit and tick "Add python.exe to PATH":
  echo   https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
  echo.
  echo Then CLOSE this window, open a NEW one, and run BUILD_WINDOWS8.bat again.
  echo ^(Administrator is NOT required.^)
  goto :fail
)

call :log Using interpreter: %PYTHON_EXE%
"%PYTHON_EXE%" -c "import sys; print(sys.version)"
if errorlevel 1 (
  call :log [ERROR] Could not run the Python executable.
  goto :fail
)

"%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if (3,8) <= sys.version_info[:2] <= (3,10) else 1)"
if errorlevel 1 (
  call :log [ERROR] Wrong Python version — need 3.8, 3.9, or 3.10
  echo.
  echo [ERROR] This Python is NOT 3.8–3.10.
  "%PYTHON_EXE%" -c "import sys; print('Found:', sys.version)"
  echo.
  echo Python 3.11+ cannot install PySide2 ^(required for Windows 8^).
  echo Install Python 3.10.11 and run this script again.
  goto :fail
)

REM --- Recreate venv if missing or built with wrong/foreign Python ---
set "NEED_VENV=0"
if not exist "venv\Scripts\python.exe" set "NEED_VENV=1"
if exist "venv\bin\python" set "NEED_VENV=1"

if "%NEED_VENV%"=="0" (
  "venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if (3,8) <= sys.version_info[:2] <= (3,10) else 1)" >nul 2>&1
  if errorlevel 1 set "NEED_VENV=1"
)

if "%NEED_VENV%"=="1" (
  call :log Recreating venv with %PYTHON_EXE%
  echo.
  echo === Creating virtual environment ===
  if exist "venv" (
    call :log Removing old venv folder
    rmdir /s /q "venv" 2>nul
  )
  "%PYTHON_EXE%" -m venv venv
  if errorlevel 1 (
    call :log [ERROR] venv creation failed
    echo [ERROR] Could not create venv.
    echo Try: "%PYTHON_EXE%" -m pip install virtualenv
    goto :fail
  )
) else (
  call :log Reusing existing venv\Scripts\python.exe
)

if not exist "venv\Scripts\python.exe" (
  call :log [ERROR] venv\Scripts\python.exe missing after create
  goto :fail
)

set "VPY=%CD%\venv\Scripts\python.exe"
call :log Venv python: %VPY%

echo.
echo === Upgrading pip / setuptools ===
"%VPY%" -m pip install --upgrade "pip<25" "setuptools<70" wheel >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] pip upgrade failed — see build_log.txt
  echo [ERROR] pip upgrade failed. See build_log.txt
  goto :fail
)

echo.
echo === Installing requirements-win8.txt ^(this can take several minutes^) ===
"%VPY%" -m pip install -r requirements-win8.txt >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] pip install failed — see build_log.txt
  echo.
  echo [ERROR] pip install failed.
  echo Open build_log.txt in this folder for the full error.
  echo Common causes:
  echo   - Not Python 3.8–3.10
  echo   - No internet on the build PC
  echo   - Corporate proxy blocking PyPI
  goto :fail
)

echo.
echo === Checking PySide2 ===
"%VPY%" -c "import PySide2; print('PySide2 OK', PySide2.__version__)"
if errorlevel 1 (
  call :log [ERROR] PySide2 import failed
  echo [ERROR] PySide2 did not import. See build_log.txt
  goto :fail
)

echo.
echo === Running PyInstaller ^(several minutes^) ===
"%VPY%" -m PyInstaller --noconfirm --clean packaging\InventoryManager.spec >> "%LOG%" 2>&1
if errorlevel 1 (
  call :log [ERROR] PyInstaller failed — see build_log.txt
  echo [ERROR] PyInstaller failed. Open build_log.txt for details.
  goto :fail
)

echo.
echo === Post-build: flatten Qt plugins ===
"%VPY%" packaging\post_build_flatten.py
if errorlevel 1 (
  call :log [ERROR] post_build_flatten failed
  goto :fail
)

echo.
echo === Post-build: VC++ DLLs + START_HERE.bat ===
"%VPY%" packaging\copy_vcruntime.py

if not exist "dist\InventoryManager\backups" mkdir "dist\InventoryManager\backups"
if not exist "dist\InventoryManager\logs" mkdir "dist\InventoryManager\logs"
if not exist "dist\InventoryManager\assets" mkdir "dist\InventoryManager\assets"
if not exist "dist\InventoryManager\icons" mkdir "dist\InventoryManager\icons"

if not exist "dist\InventoryManager\InventoryManager.exe" (
  call :log [ERROR] exe missing after build
  echo [ERROR] dist\InventoryManager\InventoryManager.exe was not created.
  goto :fail
)

call :log BUILD OK
echo.
echo ============================================================
echo  BUILD OK
echo.
echo  Copy this ENTIRE folder to the USB stick:
echo      %CD%\dist\InventoryManager\
echo.
echo  On Windows 8: double-click InventoryManager.exe
echo  Full log: %LOG%
echo ============================================================
echo.
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  BUILD FAILED — window left open on purpose
echo  Read the messages above, and open:
echo      %LOG%
echo ============================================================
echo.
pause
exit /b 1

:log
echo %* >> "%LOG%"
echo %*
goto :eof
