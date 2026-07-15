@echo off
REM Opens a console that never closes by itself — use this if the
REM normal BUILD_WINDOWS8.bat window still flashes and disappears.
cd /d "%~dp0"
cmd /k "BUILD_WINDOWS8.bat & echo. & echo Finished. Type exit to close."
