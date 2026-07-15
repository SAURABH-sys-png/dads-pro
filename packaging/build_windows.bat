@echo off
REM Thin wrapper — prefer BUILD_WINDOWS8.bat from the project root.
REM Kept so older docs still work. Always pauses on failure/success via parent.
cd /d "%~dp0.."
if not exist "BUILD_WINDOWS8.bat" (
  echo [ERROR] BUILD_WINDOWS8.bat not found in project root.
  pause
  exit /b 1
)
call BUILD_WINDOWS8.bat
exit /b %ERRORLEVEL%
