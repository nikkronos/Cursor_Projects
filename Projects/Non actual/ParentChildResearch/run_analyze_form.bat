@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo АНАЛИЗ СТРУКТУРЫ GOOGLE FORM
echo ========================================
echo.
echo Выберите режим:
echo 1. Автоматический (попытка автоматического заполнения)
echo 2. Ручной (вы вручную переходите между страницами)
echo.
set /p mode="Введите номер режима (1 или 2): "

if "%mode%"=="2" (
    python scripts\analyze_form_structure.py --manual
) else (
    python scripts\analyze_form_structure.py
)
pause

