@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo СОЗДАНИЕ ПОЛНОГО ИТОГОВОГО ОТЧЁТА
echo ========================================
echo.
python create_complete_report.py
echo.
echo ========================================
pause
