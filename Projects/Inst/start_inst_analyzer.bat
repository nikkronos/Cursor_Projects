@echo off
setlocal

REM Always run from this script directory.
cd /d "%~dp0"

echo Starting Inst Analyzer on http://127.0.0.1:8000 ...
python -m uvicorn app.main:app --reload

if errorlevel 1 (
  echo.
  echo Failed to start analyzer. Check Python installation and dependencies.
  pause
)

endlocal
