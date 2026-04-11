@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo ИСПРАВЛЕНИЕ ДОКУМЕНТА v6 -^> v7
echo ========================================
echo.
echo Шаг 1: Основные исправления...
python FINAL_FIX_SCRIPT.py
echo.
echo Шаг 2: Анализ литературы...
python analyze_literature.py
echo.
echo ========================================
echo ГОТОВО!
echo ========================================
pause





